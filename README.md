# Babble

핸드폰 타자를 치는 것에 피로감을 느끼는 사람들을 위해 오디오를 기반으로 트위터같은 SNS를 만들면 어떨까하는 생각에 시작한 프로젝트입니다.

## 사용한 기술스택

Django, Django restframework, Drf spectacular, Drf simple jwt, Django channels, ELK stack, whisper model, konlpy, koelectra

## 구현기능

- babbles
    - 생성, 검색, 수정, 삭제, 업데이트, 오디오에서 키워드 추출, 추출한 키워드들은 tag로 저장
- comments
    - 생성, 검색, 수정, 삭제, 업데이트
- core
    - 가입, 로그인
- followers
    - 생성, 삭제
- likes
    - 생성, 삭제, 유저가 좋아요 누른 게시물 리스트 조회
- notifications
    - 한 유저의 안읽은 알림 리스트 조회
- rebabbles
    - 생성, 삭제, 유저가 리배블한 게시물 리스트 조회
- tags
    - 특정 태그를 가지고 있는 게시물 리스트 조회
- users
    - 조회, 업데이트, 삭제, 비밀번호 변경
    

## 문제해결

1. 오디오를 텍스트로 변환하고 변환된 텍스트에서 감정과 키워드를 추출하는 작업을 외부 api를 사용해서 개발했으나, 속도도 너무 느리고 외부 api가 많으면 그만큼 의존도가 높아져 지속적인 개발에 위험이 있다 판단해 공개된 인공지능들을 사용해 의존도를 낮췄습니다.
2. 리퀘스트의 요청자가 모델의 유저와 다르면 읽기만 허용해주는 권한을 설정하고 싶었으나 장고에서는 기본적으로 제공하지 않아 직접 만들었습니다.
    - 코드
        
        ```python
        from rest_framework import permissions
        
        class IsOwnerOrReadOnly(permissions.BasePermission):
        
            def has_object_permission(self, request, view, obj):
                # 읽기 권한 요청이 들어오면 허용
                if request.method in permissions.SAFE_METHODS:
                    return True
                
                # 요청자(request.user)가 객체(Blog)의 user와 동일한지 확인
                return obj.user == request.user
        ```
        
3. whisper.py에서 외부라이브러리 import whisper가 안되는 오류가 발생했습니다. 파일 이름을 수정하니 해결되었습니다.
4. 문자열 기반 필드에 null=True 옵션을 넣었더니 빈 문자열이 아닌 None으로도 저장되는 오류가 발생해null=True를 지워서 해결했습니다.
5. 처음엔 한 유저가 게시물을 작성하면 db에 저장되고 게시물을 조회할 때 한 유저가 팔로우하는 유저들을 전부 조회하고 그 유저들의 게시물을 가져오는 방식으로 만들었습니다. 그런데 읽기 작업이 굉장히 많은 SNS 특성상 이 구조가 좋지 못하다 생각해 트위터의 구조를 보고 캐시를 적용했습니다.
    - 캐시 적용 전
        
        ![noncache](https://user-images.githubusercontent.com/53591258/228713265-4b42ed54-0fc0-4da0-b722-f1d56b03a68a.png)
        
    - 캐시 적용 후
        
        ![cache](https://user-images.githubusercontent.com/53591258/228713305-a2d3bdf3-04b3-474e-9852-782df191e122.png)
        
6. RuntimeError: Model class project.models.User doesn't declare an explicit app_label and isn't in an application in INSTALLED_APPS. 이라는 오류가 발생해 유저 모델에 다음 코드를 추가했습니다.
    - 코드
        
        ```python
        class User(models.Model):
            # fields and methods here
        
            class Meta:
                app_label = 'your_app_label'
        ```
        
7. django.db.migrations.exceptions.InconsistentMigrationHistory: Migration admin.0001_initial is applied before its dependency users.0001_initial on database 'default'. 이라는 오류가 발생해 installed app에서 admin비활성화 후 마이그레이션 실행 후 다시 활성화 다시 마이그레이션했습니다.
8. 게시물 조회에서 N+1 문제가 발생했으나 select_related와 prefetch_related를 사용해 해결했습니다.
    - 문제 코드
        
        ```python
        babbles = Babble.objects.filter(
                Q(user__in=user.self.all().values_list("following", flat=True)) | Q(user=user)
            ).order_by("-created")[start:end]
        ```
        
        | Type | Database | Reads | Writes | Totals | Duplicates |
        | --- | --- | --- | --- | --- | --- |
        | RESP | default | 44 | 0 | 44 | 41 |
        | ------ | ----------- | ---------- | ---------- | ---------- | ------------ |
        | Total queries: 44 in 0.0682s |  |  |  |  |  |
    - 해결 코드
        
        ```python
        followings = user.self.all().values_list("following__id", flat=True)
        
            babbles = (
                Babble.objects.filter(Q(user__in=followings) | Q(user=user))
                .select_related("user")
                .prefetch_related("tags")
                .order_by("-created")[start:end]
            )
        ```
        
        | Type | Database | Reads | Writes | Totals | Duplicates |
        | --- | --- | --- | --- | --- | --- |
        | RESP | default | 5 | 0 | 5 | 0 |
        | ------ | ----------- | ---------- | ---------- | ---------- | ------------ |
        | Total queries: 5 in 0.0456s |  |  |  |  |  |
9. 새로운 기능을 추가하면 제대로 구동이 되는지 화면상에서 하나하나 눌러보며 테스트를 하다가 너무 불편하고 비효율적이라 느껴 테스트코드를 작성하기 시작했습니다. 총 62개의 테스트 코드를 작성했습니다.
