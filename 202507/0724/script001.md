# 파일 생성 후 자동으로 GitHub에 Push하는 방법

파일을 생성하고 자동으로 GitHub 저장소에 푸시하는 과정을 자동화하는 방법을 단계별로 설명드리겠습니다.

## 1. 기본 준비 사항

1. **Git 설치**: 시스템에 Git이 설치되어 있어야 합니다.
   ```bash
   git --version
   ```

2. **GitHub 계정 설정**: GitHub 계정이 있고 SSH 키가 설정되어 있어야 합니다.

## 2. 로컬 저장소 설정

1. **새 디렉토리 생성 및 초기화**:
   ```bash
   mkdir my-project
   cd my-project
   git init
   ```

2. **GitHub에 새 저장소 생성**: GitHub 웹사이트에서 빈 저장소를 만듭니다.

3. **원격 저장소 연결**:
   ```bash
   git remote add origin git@github.com:your-username/your-repo.git
   ```

## 3. 파일 생성 및 자동 푸시 스크립트

### 방법 1: Bash 스크립트 사용

`push_automation.sh` 파일 생성:
```bash
#!/bin/bash

# 파일 생성 (예시: 현재 날짜를 포함한 파일)
filename="auto_file_$(date +%Y%m%d_%H%M%S).txt"
echo "This is an automatically generated file created at $(date)" > $filename

# Git 작업
git add .
git commit -m "Automated commit: added $filename"
git push origin main
```

스크립트 실행 권한 부여:
```bash
chmod +x push_automation.sh
```

### 방법 2: Python 스크립트 사용

`auto_push.py` 파일 생성:
```python
import os
from datetime import datetime

# 파일 생성
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"auto_file_{timestamp}.txt"
with open(filename, 'w') as f:
    f.write(f"Automatically generated file created at {datetime.now()}")

# Git 명령 실행
os.system('git add .')
os.system(f'git commit -m "Automated commit: added {filename}"')
os.system('git push origin main')
```

## 4. 자동화 실행 방법

1. **수동 실행**: 필요할 때마다 스크립트 실행
   ```bash
   ./push_automation.sh
   # 또는
   python auto_push.py
   ```

2. **크론 작업으로 자동화 (Linux/macOS)**:
   ```bash
   crontab -e
   ```
   다음 내용 추가 (매일 오전 9시 실행 예시):
   ```
   0 9 * * * /path/to/your/push_automation.sh
   ```

3. **Git Hooks 사용** (특정 이벤트 시 자동 실행):
   `.git/hooks/post-commit` 파일 생성:
   ```bash
   #!/bin/sh
   git push origin main
   ```
   실행 권한 부여:
   ```bash
   chmod +x .git/hooks/post-commit
   ```

## 5. 주의사항

1. **인증 문제**: HTTPS 대신 SSH를 사용하는 것이 더 안전합니다.
2. **충돌 방지**: 자동 푸시 전에 pull을 먼저 하는 것이 좋습니다.
3. **보안**: 스크립트에 GitHub 토큰이나 비밀번호를 하드코딩하지 마세요.
4. **테스트**: 실제 사용 전 테스트 저장소에서 충분히 테스트하세요.

## 6. 고급 방법: GitHub Actions 사용

GitHub 저장소에 `.github/workflows/auto-push.yml` 파일 생성:
```yaml
name: Auto File Creation and Push

on:
  schedule:
    - cron: '0 9 * * *'  # 매일 오전 9시 실행
  workflow_dispatch:     # 수동 실행 가능

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Create file
      run: |
        echo "Automatically generated at $(date)" > auto_file_$(date +%Y%m%d).txt
    - name: Commit and push
      run: |
        git config --global user.name "GitHub Actions"
        git config --global user.email "actions@github.com"
        git add .
        git commit -m "Automated file creation"
        git push
```

이 방법은 GitHub의 서버에서 직접 실행되며 별도의 로컬 설정이 필요 없습니다.

어떤 방법이 더 적합한지, 또는 특정 환경에 대한 더 자세한 설명이 필요하시면 알려주세요!
