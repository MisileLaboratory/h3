{ config, pkgs, catppuccin, ... }:
let
  c = import ./config.nix;
in
{
  home.username = "misile";
  home.homeDirectory = "/home/misile";
  home.stateVersion = "23.11"; # dont change it

  home.packages = with pkgs; [
    # System
    topgrade sbctl tealdeer synology-drive-client bluez brightnessctl gnupg

    # Development
    git niv cabal-install pkg-config edgedb fh nixpkgs-fmt
    hub poetry d2 micromamba pdm mypy dvc snyk ghidra pwndbg
    #cargo-update

    # Some cryptos
    solana-validator

    # Language compiler and lsp
    ghc
    rustup
    go
    temurin-bin-21
    python312Full
    nasm

    # Utils
    file wget imagemagick usbutils axel onefetch fastfetch ouch wgetpaste
    hyperfine hdparm duperemove hydra-check glow obs-studio virt-manager
    killall delta qemu

    # Network
    dhcpcd cloudflare-warp trayscale tor-browser-bundle-bin

    # Fonts
    fira-code-nerdfont nanum pretendard noto-fonts-color-emoji

    # Sound
    pulsemixer galaxy-buds-client mpv

    # Some chat and game
    irssi ferium vesktop
    (tetrio-desktop.override {
      withTetrioPlus = true;
    })

    # Compatibility
    figma-linux wineWowPackages.stable appimage-run
    (pkgs.writeShellScriptBin "discord" ''
      exec ${pkgs.vesktop}/bin/vesktop --enable-features=UseOzonePlatform --ozone-platform=wayland
    '')
    (pkgs.writeShellScriptBin "vscode" ''
      exec ${pkgs.vscodium}/bin/codium --enable-features=UseOzonePlatform --ozone-platform=wayland
    '')
    (pkgs.writeShellScriptBin "gdb" ''
      exec ${pkgs.pwndbg}/bin/pwndbg
    '')
    (pkgs.writeShellScriptBin "pwntools-gdb" ''
      exec ${pkgs.pwndbg}/bin/pwndbg
    '')
  ]
  ++ (with llvmPackages_latest; [clangUseLLVM openmp libunwind]) # llvm
  ++ (with nodePackages_latest; [nodejs pnpm]) # nodejs
  ++ (with python311Packages; [pip virtualenv pipx]); # python thing

  home.file = {
    ".local/share/rofi/themes/catppuccin-mocha.rasi".source = config.lib.file.mkOutOfStoreSymlink "${builtins.fetchGit{
      url="https://github.com/catppuccin/rofi";
      rev="5350da41a11814f950c3354f090b90d4674a95ce";
    }}/basic/.local/share/rofi/themes/catppuccin-mocha.rasi";
    "non-nixos-things/catppuccin-ghidra".source = config.lib.file.mkOutOfStoreSymlink "${builtins.fetchGit{
      url="https://github.com/StanlsSlav/ghidra";
      rev="f783b5e15836964e720371c0da81819577dd2614";
    }}";
  };

  home.sessionVariables = {
    QT_QPA_PLATFORM = "wayland";
    EDITOR = "nvim";
  };

  catppuccin.flavour = "mocha";
  fonts.fontconfig.enable = true;
  nixpkgs.config.allowUnfree = true;
  xdg = {
    enable = true;
    portal = {
      enable = true;
      extraPortals = with pkgs; [xdg-desktop-portal-wlr xdg-desktop-portal-gtk];
      config.common.default = ["gtk" "wlr"];
    };
  };
  gtk = {enable = true;catppuccin.enable = true;};
  programs = {
    vscode = {
      enable = true;
      package = pkgs.vscodium;
    };
    direnv = {
      enable = true;
      nix-direnv.enable = true;
    };
    eza.enable = true;
    bat = {
      enable = true;
      catppuccin.enable = true;
    };
    btop = {
      enable = true;
      catppuccin.enable = true;
    };
    fish = {
      enable = true;
      shellInit = ''
        fish_add_path -m ~/.cargo/bin
        fish_add_path -m ~/.avm/bin
        
        alias nix-clean="nix store optimise && sudo nix store optimise && nix-collect-garbage -d && sudo nix-collect-garbage -d"
        alias cat="bat"
        alias ocat="${pkgs.coreutils}/bin/cat"
        alias ls="eza --icons"
        alias onefetch="onefetch --number-of-languages 10000"
        function fzfp
          if set -q argv[1]
            $argv (${pkgs.fzf} --preview 'bat --color=always --style=numbers --line-range :500 {}')
          else
            ${pkgs.fzf} --preview 'bat --color=always --style=numbers --line-range :500 {}'
          end
        end
        function git-bulk-pulls
          if not set -q argv[1]
            set args .
          else
            set args $argv
          end
          for j in $args
            for i in $j/*
              cd $i
              git pull
              cd -
            end
          end
        end
      '';
    };
    atuin = {
      enable = true;
      enableFishIntegration = true;
    };
    git = {
      enable = true;
      lfs.enable = true;
      signing = {key = "138AC61AE9D8D2D55EAE4995CD896843C0CB9E63";signByDefault=true;};
      userName = "misilelab";
      userEmail = "misileminecord@gmail.com";
      extraConfig = { pull = {rebase = false; };
      safe = { directory = "*"; };
      init = {defaultBranch = "main";};
      delta.enable = true;
      };
    };
  };  

  # Let Home Manager install and manage itself.
  programs.home-manager.enable = true;
}
