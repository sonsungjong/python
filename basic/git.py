'''
git 설치

git config --global user.email "깃허브이메일"
git config --global user.name "깃허브이름"

git init
git add 파일명.확장자
git add .
git commit -m "날짜 버전 메모"

git status
git log --all --oneline
git log --oneline --all --graph

git diff
git difftool
git difftool 커밋아이디
git difftool 커밋아이디1 커밋아아디2

git branch "브런치명"
git switch "브런치명"
git status
git switch "master"
git merge "가져올브랜치"
git merge --no-ff "가져올브랜치"
git branch -d "머지 후 삭제할브랜치"
git branch -D "잘못만들어 삭제할 브랜치"

==충돌난 부분은 제거==
git add .
git commit -m "머지 후 충돌해결 완료"

git switch "신규 브랜치"
git rebase "메인 브랜치"
git switch "메인 브랜치"
git merge "가져올 신규 브랜치"

git merge --squash "가져올 브랜치"
안중요한 브랜치는 squash, 특정 중요한 브랜치는 3-way merge
'''
# git add : 레포지토리에 저장할 파일을 스테이징함
# git commit : 스테이징된 파일을 레포지토리에 저장
# git status : 어떤 파일들을 스테이징 해놓았는지 확인
# git log --all --oneline : commit 을 조회

# git diff : 최근 commit 과 현재 파일의 차이점을 보여줌
# git difftool : 최근 commit 과 현재 파일의 차이점을 좀더 시각적으로 좋게 보여줌 (:q 또는 :qa 를 입력하여 종료, hjkl 로 커서 이동)
# git difftool 커밋아이디 : 현재 파일과 특정 commit 의 파일 내용을 비교
# git difftool 커밋아이디1 커밋아이디2 : 커밋아이디1 때의 파일 내용과 커밋아이디2 때의 파일 내용을 비교

# 브랜치 : commit의 복사본 (메인 프로젝트를 브랜치에 복사해서 작업하여 메인 보호)
# git branch "브랜치명"
# git switch "브랜치명"
# git switch master
# git merge "가져올 브랜치" : 충돌이 나면 수동으로 제거해주고 add와 commit
# git merge --no-ff "가져올 브랜치" : 무조건 3-way-merge로 작업 (fast-forward merge방지)
# git branch -d "머지 후 삭제할 브랜치"
# git branch -D "잘못 만들어 삭제할 브랜치"

# git rebase : 메인 브랜치의 최종 commit에 가져올 브랜치를 이어붙임
# git merge --squash "가져올 브랜치" : 신규 브랜치에 대한 쓸데없는 커밋내용은 잘라버림
