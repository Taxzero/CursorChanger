; === Mabinogi Cursor Installer (User-mode) ===
[Setup]
AppName=Mabinogi Cursor
AppVersion=1.0
; 사용자 AppData\Local\MabinogiCursor에 설치
DefaultDirName={localappdata}\MabinogiCursor
DefaultGroupName=MabinogiCursor
UninstallDisplayIcon={app}\mabinogiCursor.exe
; 설치 경로 고정
DisableDirPage=yes
; 관리자 권한 없이 설치
PrivilegesRequired=lowest
OutputDir=dist_installer
OutputBaseFilename=MabinogiCursorInstaller
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\mabinogiCursor.exe";        DestDir: "{app}";               Flags: ignoreversion
Source: "custom_cursors\*";               DestDir: "{app}\custom_cursors"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Mabinogi Cursor 실행";     Filename: "{app}\mabinogiCursor.exe"
Name: "{group}\제거";                    Filename: "{uninstallexe}"
; 부팅 시 자동 실행용 바로가기(중복 생성 방지)
Name: "{userstartup}\MabinogiCursor";    Filename: "{app}\mabinogiCursor.exe"; Check: not FileExists(ExpandConstant('{userstartup}\MabinogiCursor.lnk'))

[Run]
Filename: "{app}\mabinogiCursor.exe"; Description: "설치 후 바로 실행"; Flags: nowait postinstall skipifsilent
