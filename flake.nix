{
  description = "williamdemeo.github.io: MkDocs Material site, dev shell, and strict build";

  # Why a channel tarball rather than `github:NixOS/nixpkgs/nixos-25.05`:
  #
  #   * channels.nixos.org redirects to an immutable
  #     releases.nixos.org/nixos/25.05/nixos-25.05.<build> path, which
  #     flake.lock records together with its narHash.  This is pinned exactly
  #     as tightly as a `github:` ref -- see the `locked` entry in flake.lock.
  #   * That build is a *channel* build: it passed the nixpkgs test suite and
  #     is fully populated in cache.nixos.org, so CI substitutes binaries
  #     instead of compiling Cairo from source.
  #   * It never touches the GitHub API, which rate-limits unauthenticated
  #     Actions runners.
  #
  # `nix flake update` advances to the current channel build.  Switching to
  # `github:NixOS/nixpkgs/nixos-25.05` is a one-line change if preferred.
  inputs.nixpkgs.url = "https://channels.nixos.org/nixos-25.05/nixexprs.tar.xz";

  outputs =
    { self, nixpkgs }:
    let
      lib = nixpkgs.lib;

      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];

      forEachSystem = f: lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});

      # Only the files the build actually reads.  csp/, archive/, the CV and
      # git history stay out of the store, so touching them does not
      # invalidate a build that cannot possibly depend on them.
      siteSource = lib.fileset.toSource {
        root = ./.;
        fileset = lib.fileset.unions [
          ./mkdocs.yml
          ./docs
          # theme.custom_dir.  Leaving it out builds a site that silently
          # loses the override, which is the sort of difference between the
          # Nix build and `make build` this fileset exists to prevent.
          ./overrides
          # Where the mkdocs hooks and page generators live.  mkdocs.yml's
          # `hooks:` key points at scripts/python/redirects_hook.py and
          # scripts/python/recent_posts_hook.py.
          ./scripts/python
          # Read by that hook to emit the legacy-URL redirect stubs (#15).
          ./redirects.yml
        ];
      };

      # The math audit needs scripts/js, which the site build never reads.
      # Kept out of siteSource for the same reason as below: adding it there
      # would make editing the audit script invalidate a site build that
      # cannot depend on it.  docs/ is here for all three of its roles at once
      # -- the pages to audit, the KaTeX bundle to render them with, and the
      # macro table both of those share.
      mathSource = lib.fileset.toSource {
        root = ./.;
        fileset = lib.fileset.unions [
          ./docs
          ./scripts/js
        ];
      };

      # check-redirect-map needs more than the site build does: the two legacy
      # URL inventories, and the imported Zola trees it re-derives the Zola one
      # from.  Kept separate so those 7 MB stay out of the site build's inputs,
      # where a change to them would invalidate a build that cannot read them.
      redirectSource = lib.fileset.toSource {
        root = ./.;
        fileset = lib.fileset.unions [
          ./redirects.yml
          ./scripts/python
          ./import/legacy-urls
          ./import/zola-content
          ./import/zola-converted
          ./archive/octopress/urls.txt
          # The checker resolves internal redirect targets against docs/.
          # Every target is external today, so leaving this out would go
          # unnoticed until the first internal one -- which would then be
          # reported as missing rather than checked.
          ./docs
        ];
      };

      # gen_publications.py --check compares every committed output against a
      # fresh render, so it needs the bibliography and those outputs as well as
      # the scripts -- and it needs them laid out as they are in the repository,
      # because the script finds them relative to its own location.  A generated
      # file missing from this list is not checked, and nothing would say so.
      #
      # ./cv is the fourth output, cv/publications.typ, which the CV's PDF reads
      # (ADR-010).  It is a whole directory rather than that one file because
      # the two beside it are the CV's own generated source and its template,
      # and a fileset naming one generated file in a directory of them is the
      # shape this comment exists to warn about.
      bibliographySource = lib.fileset.toSource {
        root = ./.;
        fileset = lib.fileset.unions [
          ./bibliography.json
          ./scripts/python
          ./docs/_snippets
          ./docs/publications.bib
          ./cv
        ];
      };

      # gen_cv.py --check --pdf re-renders the page and the Typst source from
      # cv.yml, then recompiles the PDF and compares its bytes, so it needs all
      # of the files it writes and the ones it reads.  DeMeo-CV.pdf is named
      # rather than the whole of docs/assets: it is the one generated file under
      # there that this check is about, and the KaTeX bundle beside it has no
      # business invalidating a CV render.  Comparing it against a fresh compile
      # is the only thing that keeps it from drifting from cv.yml (ADR-010).
      #
      # The publications snippet is not read by this script -- the page includes
      # it at build time and the PDF imports cv/publications.typ -- but
      # docs/_snippets is in `bibliographySource` above, which is where that
      # file is checked.
      cvRenderSource = lib.fileset.toSource {
        root = ./.;
        fileset = lib.fileset.unions [
          ./cv.yml
          ./cv
          ./scripts/python
          ./docs/cv.md
          ./docs/assets/DeMeo-CV.pdf
        ];
      };

      # check_cv_sources.py reads cv.yml, the four CV copies, the committed
      # inventory it compares its own extraction against, and bibliography.json
      # -- publications live there (ADR-006) and are covered from there, which
      # is what makes the boundary between the two files checkable.  docs/cv.md
      # is one of the four copies, so docs/ is here for that one file; the
      # script finds everything relative to its own location, so the layout has
      # to match the repository's.
      cvSource = lib.fileset.toSource {
        root = ./.;
        fileset = lib.fileset.unions [
          ./cv.yml
          ./bibliography.json
          ./scripts/python
          ./import/legacy-cv
          ./import/zola-content/cv
          ./docs/cv.md
        ];
      };

      # The worktree tooling builds the repositories it tests against in
      # $TMPDIR, so its check needs the scripts and nothing else from here --
      # not even git history, and certainly not the network.
      worktreeSource = lib.fileset.toSource {
        root = ./.;
        fileset = ./scripts/git;
      };

      # A dirty tree is normal during editing, so fall back rather than fail.
      revision = self.shortRev or self.dirtyShortRev or "dirty";

      perSystem = pkgs: rec {
        # mkdocs-material: nixpkgs 25.05 ships 9.6.4 while requirements.txt
        # pins 9.5.49.  Overriding the version here rather than bumping
        # requirements.txt keeps both paths on the same release without
        # smuggling a theme upgrade into an infrastructure change.  The two
        # are held together by checks.requirements-pins, which fails the
        # build if they ever drift.
        #
        # nixpkgs builds this from a GitHub tag; the PyPI sdist carries the
        # same prebuilt `material/` tree plus the requirements.txt and
        # package.json its hatch build hooks read.
        mkdocs-material = pkgs.python3Packages.mkdocs-material.overridePythonAttrs (_: rec {
          version = "9.5.49";
          src = pkgs.python3Packages.fetchPypi {
            pname = "mkdocs_material";
            inherit version;
            hash = "sha256-NnG7KCtPU6HHLgitvgTSSBqY+F/tOSUwBR+A/5SpYh0=";
          };
        });

        pythonEnv = pkgs.python3.withPackages (
          ps:
          [
            ps.mkdocs
            mkdocs-material
          ]
          # Pillow and CairoSVG.  Not needed by today's mkdocs.yml, but they
          # are what the `social` plugin imports in M3-5, and pulling them in
          # now is what makes checks.native-deps meaningful.
          ++ mkdocs-material.optional-dependencies.imaging
        );

        # Cairo and Pango reach the Python layer through cffi/ctypes rather
        # than a link-time dependency, which is why the pip path needs a
        # matching `apt-get install` and this one does not: nixpkgs patches
        # cairocffi to dlopen an absolute store path.  Listing them keeps
        # them in the closure and available to anything else in the shell.
        nativeLibs = with pkgs; [
          cairo
          pango
          gdk-pixbuf
          freetype
          fontconfig
          libffi
        ];

        # Social cards rasterise text, so a font has to exist -- the third
        # leg of the works-locally-fails-in-CI problem, after Cairo and
        # Pango.  Roboto is Material's default family; DejaVu covers the
        # glyphs Roboto does not.
        fonts = with pkgs; [
          roboto
          dejavu_fonts
        ];

        fontsConf = pkgs.makeFontsConf { fontDirectories = fonts; };

        site = pkgs.stdenvNoCC.mkDerivation {
          pname = "williamdemeo-site";
          version = revision;
          src = siteSource;

          nativeBuildInputs = [ pythonEnv ];
          buildInputs = nativeLibs;

          FONTCONFIG_FILE = fontsConf;

          dontConfigure = true;

          buildPhase = ''
            runHook preBuild

            # mkdocs and the social plugin cache under $HOME, which does not
            # exist in the sandbox.
            export HOME="$TMPDIR"

            # --strict promotes warnings to errors, so a dangling internal
            # link fails here exactly as it does in `make check`.
            mkdocs build --strict --site-dir "$out"

            runHook postBuild
          '';

          # buildPhase already wrote $out, and the output is HTML: there are
          # no shebangs or RPATHs to rewrite.
          dontInstall = true;
          dontFixup = true;

          meta = {
            description = "Generated williamdemeo.github.io site";
            homepage = "https://williamdemeo.github.io/";
          };
        };
      };
    in
    {
      packages = forEachSystem (
        pkgs:
        let
          inherit (perSystem pkgs) site;
        in
        {
          inherit site;
          default = site;
        }
      );

      devShells = forEachSystem (
        pkgs:
        let
          this = perSystem pkgs;
        in
        {
          default = pkgs.mkShellNoCC {
            name = "williamdemeo-site";

            packages = [
              this.pythonEnv
              pkgs.gnumake
              # fc-match, fc-list: the quickest way to tell whether a missing
              # glyph is a font problem or a Cairo problem.
              pkgs.fontconfig
              # `make cv-pdf` (ADR-010).  One store path, 11.5 MiB to fetch,
              # and it brings its own fonts -- which is why the CV's template
              # asks for none from the system and the PDF is reproducible.
              pkgs.typst
            ]
            ++ this.nativeLibs;

            FONTCONFIG_FILE = this.fontsConf;

            # The Makefile reads this to skip its virtualenv bootstrap, since
            # reinstalling MkDocs from PyPI inside a shell that already
            # provides it defeats the point.  A marker of our own rather than
            # IN_NIX_SHELL, which is set inside unrelated shells too --
            # `nix-shell -p jq` would claim MkDocs is on PATH when it is not.
            SITE_NIX_SHELL = 1;

            # For a human at a prompt only: `nix develop --command` and CI
            # should not get a banner prepended to their output.
            shellHook = ''
              if [ -t 1 ]; then
                echo "mkdocs $(mkdocs --version | sed 's/.*version //')"
                echo "make serve | make check | make build"
              fi
            '';
          };
        }
      );

      checks = forEachSystem (
        pkgs:
        let
          this = perSystem pkgs;
        in
        {
          # `nix flake check` runs the strict build, so CI and `make check`
          # and a local `nix build` are all the same derivation.
          site = this.site;

          # The dependency this whole flake exists for.  Renders text through
          # CairoSVG and loads a TrueType face through Pillow, which is the
          # Cairo/Pango/fontconfig/FreeType path the `social` plugin takes in
          # M3-5.  If this passes in CI, social cards will not fail there for
          # a missing system library.
          native-deps = pkgs.runCommandLocal "check-native-deps"
            {
              nativeBuildInputs = [
                this.pythonEnv
                pkgs.fontconfig
              ];
              buildInputs = this.nativeLibs;
              FONTCONFIG_FILE = this.fontsConf;
            }
            ''
              export HOME="$TMPDIR"

              # Resolving through fontconfig rather than globbing a store path
              # checks FONTCONFIG_FILE as well as the font package itself.
              font="$(fc-match -f '%{file}' Roboto)"
              echo "fc-match Roboto -> $font"

              SOCIAL_CHECK_FONT="$font" python3 ${./nix/native-deps-check.py}
              touch "$out"
            '';

          # requirements.txt is the supported non-Nix path (ADR-004).  Two
          # dependency sets are only safe while they agree, so this fails the
          # build when they do not.
          requirements-pins = pkgs.runCommandLocal "check-requirements-pins"
            {
              nativeBuildInputs = [ this.pythonEnv ];
            }
            ''
              python3 ${./nix/requirements-pins-check.py} ${./requirements.txt}
              touch "$out"
            '';

          # Every URL the two legacy sites served is accounted for exactly
          # once in redirects.yml, the Zola inventory still corresponds 1:1
          # with the imported page tree, and every URL the map claims resolves
          # does resolve in the built site.  Depends on `site` so it checks the
          # real output rather than a rebuild of it.
          redirect-map = pkgs.runCommandLocal "check-redirect-map"
            {
              nativeBuildInputs = [ this.pythonEnv ];
            }
            ''
              python3 ${redirectSource}/scripts/python/check_redirects.py \
                --verify-inventory --site ${this.site}
              touch "$out"
            '';

          # Every expression in docs/ rendered through the KaTeX bundle the
          # site ships, with the site's own macro table.  This is the other
          # half of the pair below: that one reads source and catches what
          # renders without error and without meaning, this one renders and
          # catches what KaTeX refuses.  Neither sees the other's defects.
          #
          # node is here and nowhere else in the flake.  It is the audit's only
          # requirement -- the KaTeX bundle comes from docs/assets, not npm --
          # and it buys a guarantee that no imported LaTeX construct reaches a
          # reader as red error text.
          math-audit = pkgs.runCommandLocal "check-math-audit"
            {
              nativeBuildInputs = [ pkgs.nodejs ];
            }
            ''
              # audit_math.mjs resolves the KaTeX bundle and the macro table
              # relative to the working directory, so run it from the source.
              cd ${mathSource}
              node scripts/js/audit_math.mjs docs
              touch "$out"
            '';

          # Math source that arithmatex and KaTeX will silently mis-render:
          # `\\{` where `\{` was meant, `\_` where a subscript was meant, and
          # `$ x $`, which smart_dollar declines so the LaTeX ships as prose.
          # None of these raise, so `mkdocs build --strict` and the KaTeX
          # render audit both pass while the page is wrong on screen -- which
          # is exactly why it is worth a check of its own.
          math-source = pkgs.runCommandLocal "check-math-source"
            {
              nativeBuildInputs = [ this.pythonEnv ];
            }
            ''
              python3 ${siteSource}/scripts/python/check_math_source.py \
                ${siteSource}/docs
              touch "$out"
            '';

          # Its own rules: which backslash runs are defects and which are
          # correct LaTeX, and what counts as being inside a math span.
          math-source-tests = pkgs.runCommandLocal "check-math-source-tests"
            {
              nativeBuildInputs = [ this.pythonEnv ];
            }
            ''
              python3 ${siteSource}/scripts/python/test_math_source.py
              touch "$out"
            '';

          # The redirect map's own matching rules: exact-beats-prefix,
          # longest-prefix-wins, and the config validation that makes a
          # malformed rule fail loudly instead of silently covering nothing.
          redirect-map-tests = pkgs.runCommandLocal "check-redirect-map-tests"
            {
              nativeBuildInputs = [ this.pythonEnv ];
            }
            ''
              python3 ${redirectSource}/scripts/python/test_redirects.py
              touch "$out"
            '';

          # `git wt clean` deletes worktrees and branches, and decides what to
          # delete from four questions -- is the tree dirty, are its commits in
          # the base branch, is the remote branch still there, is anything
          # unpushed -- that no single git command answers.  Getting one wrong
          # either loses work or leaves the list as cluttered as it was before
          # the tool existed, and both failures are silent.  The test builds
          # its own remote and clones in $TMPDIR, so it needs git and nothing
          # else.
          #
          # The copy and patchShebangs are not ceremony either: the sandbox has
          # no /usr/bin/env, so a `#!/usr/bin/env bash` script is unrunnable
          # there -- the kernel reports it as "required file not found", which
          # reads like a missing script rather than a missing interpreter.  The
          # test executes git-wt the way a shell does rather than passing it to
          # bash, because that is how it is used, so the shebang has to work.
          worktree-tooling = pkgs.runCommandLocal "check-worktree-tooling"
            {
              nativeBuildInputs = [ pkgs.git ];
            }
            ''
              cp -r ${worktreeSource}/scripts/git ./git-tools
              chmod -R u+w ./git-tools
              patchShebangs ./git-tools
              bash ./git-tools/test_git_wt.sh
              touch "$out"
            '';

          # The bibliography tooling, and its output.
          #
          # `--check` is the part that guards the repository rather than the
          # scripts: docs/_snippets/ is committed, and a hand-edit to a
          # generated file passes every other gate here.  It needs no network,
          # so unlike `make publications-verify` it belongs in a sandbox.
          #
          # The tests are worth running here precisely because the verifier
          # itself cannot: it needs the publishers.  They use fixtures instead,
          # and the ones that matter prove the verifier exits non-zero when it
          # cannot reach a service rather than reporting the clean run it did
          # not earn, and that the renderer's relaxed duplicate-arXiv rule
          # still catches a real duplicate.
          # Every entry in all four legacy CV copies is either carried in
          # cv.yml or declared an omission there with a reason (ADR-003).
          #
          # This is the gate that "nothing was silently lost" rests on, and it
          # belongs here for the same reason `bibliography-tooling` does: the
          # copies are snapshotted in the repository, so it resolves nothing and
          # needs no network.  Reading them over the wire would have made it a
          # check CI could not run, which is a check that stops being run.
          #
          # The tests are not redundant with it.  A coverage checker reports
          # success when nothing is uncovered, and an extractor that has
          # quietly stopped finding entries produces exactly that; the tests
          # are what hold the failures it must still report.
          cv-sources = pkgs.runCommandLocal "check-cv-sources"
            {
              nativeBuildInputs = [ this.pythonEnv ];
            }
            ''
              python3 ${cvSource}/scripts/python/check_cv_sources.py
              python3 ${cvSource}/scripts/python/test_cv_sources.py
              touch "$out"
            '';

          # The CV page, the CV's Typst source and the PDF, all three compared
          # against a fresh render of cv.yml (ADR-010).
          #
          # The PDF is the part that needs saying.  It is committed, because the
          # page links it and the site build must not need a typesetter -- and a
          # committed binary that nothing compares against is exactly the drift
          # the two generators here exist to prevent.  So this recompiles it and
          # compares the bytes, which works because Typst's output is
          # deterministic and the build date lives in the committed .typ rather
          # than coming from the clock.  A stale PDF fails the pull request that
          # left it stale.
          #
          # It doubles as the reproducibility check: if this passes on a runner
          # and on a laptop, the two produced the same file.
          cv-render = pkgs.runCommandLocal "check-cv-render"
            {
              nativeBuildInputs = [ this.pythonEnv pkgs.typst ];
            }
            ''
              python3 ${cvRenderSource}/scripts/python/gen_cv.py --check --pdf
              touch "$out"
            '';

          bibliography-tooling = pkgs.runCommandLocal "check-bibliography-tooling"
            {
              nativeBuildInputs = [ this.pythonEnv ];
            }
            ''
              python3 ${bibliographySource}/scripts/python/gen_publications.py --check
              python3 ${bibliographySource}/scripts/python/test_gen_publications.py
              python3 ${bibliographySource}/scripts/python/test_verify_bibliography.py
              touch "$out"
            '';
        }
      );

      apps = forEachSystem (
        pkgs:
        let
          serve = {
            type = "app";
            meta.description = "Live-reloading MkDocs preview on 127.0.0.1:$PORT (default 8000)";
            program = lib.getExe (
              pkgs.writeShellApplication {
                name = "mkdocs-serve";
                runtimeInputs = [ (perSystem pkgs).pythonEnv ];
                # Run from the checkout: mkdocs picks up ./mkdocs.yml.
                text = ''
                  exec mkdocs serve --dev-addr "127.0.0.1:''${PORT:-8000}" "$@"
                '';
              }
            );
          };
        in
        {
          inherit serve;
          default = serve;
        }
      );
    };
}
