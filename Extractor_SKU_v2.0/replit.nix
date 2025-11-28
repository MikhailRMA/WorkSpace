{ pkgs }: {
  deps = [
    pkgs.chromium
    pkgs.chromedriver
    pkgs.google-chrome
    pkgs.python38
    pkgs.python38Packages.pip
    pkgs.python38Packages.virtualenv
  ];
}