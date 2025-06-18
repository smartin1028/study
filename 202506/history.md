# PowerShell로 여러 폴더 위치 자동으로 열기 방법

PowerShell을 사용하여 여러 폴더를 동시에 열 수 있는 몇 가지 방법을 소개합니다.

## 1. 기본적인 방법 (explorer 명령 사용)

```powershell
# 단일 폴더 열기
explorer "C:\경로\폴더명"

# 여러 폴더 동시에 열기
explorer "C:\경로\폴더1"; explorer "C:\경로\폴더2"; explorer "D:\다른경로\폴더3"
```

## 2. 배열과 반복문 사용

```powershell
# 폴더 경로 배열 정의
$folders = @(
    "C:\Users\사용자명\Documents",
    "D:\Projects\Project1",
    "E:\Backup\2023"
)

# 각 폴더 열기
foreach ($folder in $folders) {
    if (Test-Path $folder) {
        explorer $folder
    } else {
        Write-Warning "폴더가 존재하지 않습니다: $folder"
    }
}
```

## 3. 함수로 만들어 재사용하기

```powershell
function Open-MultipleFolders {
    param(
        [string[]]$Paths
    )
    
    foreach ($path in $Paths) {
        if (Test-Path $path -PathType Container) {
            explorer $path
        } else {
            Write-Warning "경로가 존재하지 않거나 폴더가 아닙니다: $path"
        }
    }
}

# 사용 예시
Open-MultipleFolders -Paths "C:\Windows", "C:\Temp", "D:\Downloads"
```

## 4. 특정 조건의 폴더 모두 열기

```powershell
# 특정 디렉토리 아래의 모든 하위 폴더 열기
Get-ChildItem "C:\ParentFolder" -Directory | ForEach-Object {
    explorer $_.FullName
}

# 이름에 특정 문자열이 포함된 폴더들만 열기
Get-ChildItem "C:\경로" -Directory -Filter "*프로젝트*" | ForEach-Object {
    explorer $_.FullName
}
```

## 5. PowerShell 스크립트 파일로 저장하여 사용

1. 메모장이나 VS Code 등으로 `.ps1` 파일 생성 (예: `OpenFolders.ps1`)
2. 위의 코드 중 원하는 방법을 붙여넣고 저장
3. PowerShell에서 스크립트 실행 (실행 정책 변경이 필요할 수 있음)

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser  # 한 번만 실행
.\OpenFolders.ps1
```

## 주의사항

- 경로에 공백이 포함된 경우 따옴표로 감싸야 합니다.
- 존재하지 않는 폴더를 열려고 하면 오류가 발생할 수 있으므로 `Test-Path`로 확인하는 것이 좋습니다.
- 한 번에 너무 많은 폴더를 열면 시스템 성능에 영향을 줄 수 있습니다.

원하는 방식에 따라 적절한 방법을 선택하여 사용하시면 됩니다.