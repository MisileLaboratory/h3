with import <nixpkgs> {};
  mkShell {
  nativeBuildInputs = with pkgs.buildPackages; [libseccomp autoPatchelfHook libunwind] ++
  (with python311Packages; [numpy httpx python-lsp-server 
  (pwntools.overrideAttrs(prev: {
    postFixup = "";
  }))
  beautifulsoup4 lxml loguru flask]);
  NIX_LD_LIBRARY_PATH = lib.makeLibraryPath [
    stdenv.cc.cc
    libseccomp docker-compose
  ];
  NIX_LD = lib.fileContents "${stdenv.cc}/nix-support/dynamic-linker";
  }
