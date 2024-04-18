{config, lib, pkgs, ...}:
{
  imports = [
    ./applications/yubikey.nix
  ];

  services = {
    fprintd.enable = true;
    openvpn.servers = {
      VPN = { config = '' config /home/misile/non-nixos-things/openvpns/profile.ovpn ''; autoStart = false; };
    };
    clamav = {
      daemon.enable = true;
      updater.enable = true;
    };
    tor = {
      enable = true;
      client.enable = true;
    };
    tailscale.enable = true;
  };

  systemd = {
    user = {
      services.polkit-gnome-authentication-agent-1 = {
        description = "polkit-gnome-authentication-agent-1";
        wantedBy = [ "graphical-session.target" ];
        wants = [ "graphical-session.target" ];
        after = [ "graphical-session.target" ];
        serviceConfig = {
          Type = "simple";
          ExecStart = "${pkgs.polkit_gnome}/libexec/polkit-gnome-authentication-agent-1";
          Restart = "on-failure";
          RestartSec = 1;
          TimeoutStopSec = 10;
        };
      };
    };
  };

  environment.systemPackages = with pkgs; [fprintd];
}