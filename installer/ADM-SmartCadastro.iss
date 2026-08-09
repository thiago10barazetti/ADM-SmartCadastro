#define MyAppName "ADM SmartCadastro"
#define MyAppVersion "1.0.0"
#define MyAppExeName "ADM SmartCadastro.exe"

[Setup]
AppId={{7F3F80A1-02C3-4FCE-A8B2-ADMSMARTCADASTRO}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=ADM SmartCadastro

DefaultDirName={autopf}\ADM SmartCadastro
DefaultGroupName=ADM SmartCadastro

OutputDir=output
OutputBaseFilename=ADM-SmartCadastro-Setup-1.0.0

SetupIconFile=..\assets\adm_smartcadastro.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

Compression=lzma2
SolidCompression=yes

WizardStyle=modern

PrivilegesRequired=admin

ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

DisableProgramGroupPage=yes

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar um atalho na Área de Trabalho"; GroupDescription: "Atalhos adicionais:"

[Files]
Source: "..\dist\ADM SmartCadastro\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\ADM SmartCadastro"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\ADM SmartCadastro"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir ADM SmartCadastro"; Flags: nowait postinstall skipifsilent