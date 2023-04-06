# Babble

오디오 기반의 트위터 스타일 SNS를 구상하며 시작한 프로젝트입니다.  

음성 인식 및 오디오 메시지 기능을 활용하여 사용자들이 쉽고 편리하게 소통할 수 있는 SNS 플랫폼을 구축하는 것을 목표로 합니다. 사용자들은 텍스트 대신 음성 메시지를 통해 감정, 생각, 아이디어를 표현하고 공유할 수 있게 됩니다. 이를 통해 키보드 입력에 의존하지 않고도 소통의 장벽을 극복할 수 있습니다.  

또한, 이 프로젝트는 장애인들, 특히 시각 장애인과 청각 장애인을 위한 접근성을 높이는데 기여할 수 있습니다. 시각 장애인의 경우 음성 메시지를 통한 소통이 더 쉽고 편리하며, 청각 장애인의 경우 텍스트 변환 기능을 활용하여 음성 메시지를 텍스트로 변환하여 볼 수 있게 됩니다.  

## 1. 사용한 기술스택

Django, Django REST framework, DRF spectacular, DRF simple JWT, Django channels, ELK stack, whisper model, konlpy, koelectra

## 2. 데이터베이스 설계

- `User`: 사용자 정보(Django의 AbstractUser상속)
    - id (PK): 사용자 식별자
    - username: 이메일 (unique, 이메일로 회원가입)
- `Babble`: 배블 정보
    - id (PK): 배블 식별자
    - user_id (FK): 사용자 식별자
    - audio: 오디오가 저장된 위치
    - created: 작성 시각
    - modified: 수정 시각
    - tags: 태그들 (ManyToManyField)
    - like_count: 좋아요 수
    - comment_count: 댓글 수
    - rebabble_count: 리배블 수
- `Comment`: 댓글 정보
    - id (PK): 댓글 식별자
    - user_id (FK): 작성자 식별자
    - babble_id (FK): Babble 식별자
    - audio: 댓글 오디오 파일
    - created : 작성 시각
    - modified : 수정 시각
- `Rebabble`: 리배블 정보
    - id (PK): 리배블 식별자
    - user_id (FK): 사용자 식별자
    - babble_id (FK): 배블 식별자
    - created: 작성 시각
- `Tag`: 태그 정보
    - text (PK): 태그 이름
    - created: 작성 시각
- `Notification`: 알림 정보
    - id (PK): 알림 식별자
    - recipient (FK): 받는 유저 식별자
    - sender (FK): 보배는 유저 식별자
    - message: 알림 내용
    - is_read: 확인 여부
    - created: 작성 시각
- `Like`: 좋아요 정보
    - id (PK): 좋아요 식별자
    - user_id (FK): 사용자 식별자
    - babble_id (FK): 배블 식별자
    - created: 작성 시각
- `Follower`: 팔로워 정보
    - id (PK): 팔로워 식별자
    - user_id (FK): 팔로우 하는 사용자 식별자
    - following_id (FK): 팔로우 당하는 사용자 식별자
    - created: 작성 시각

## 3. REST API 설계

- User 관련 API
    - `GET /users/<id>`: 특정 유저 조회
    - `PATCH /users/<id>`: 특정 유저 부분 업데이트
    - `DELETE /users/<id>`: 특정 유저 삭제
    - `PATCH /users/password`: 비밀번호 변경
- Auth 관련 API
    - `POST /auth/signup`: 회원가입
    - `POST /auth/signin`: 로그인
- Babble 관련 API
    - `GET /babbles`: 팔로잉 한 유저들의 배블 목록 조회
    - `POST /babbles`: 배블 생성
    - `GET /babbles/<id>`: 특정 배블 조회
    - `PATCH /babbles/<id>`: 특정 배블 수정
    - `DELETE /babbles/<id>`: 특정 배블 삭제
    - `GET /babbles/explore`: 팔로잉 하지 않은 유저들의 배블 목록 조회
    - `GET /babbles/<user_id>/profile`: 특정 유저의 배블 목록 조회
- Comment 관련 API
    - `GET /babbles/<id>/comments`: 특정 배블의 댓글 목록 조회
    - `POST /babbles/<id>/comments`: 특정 배블에 댓글 생성
    - `PATCH /babbles/<id>/comments/<id>`: 특정 배블의 특정 댓글 수정
    - `DELETE /babbles/<id>/comments/<id>`: 특정 배블의 특정 댓글 삭제
- Rebabble 관련 API
    - `GET /users/<id>/rebabbles`: 특정 유저가 리배블한 배블 목록 조회
    - `POST /babbles/<id>/rebabbles`: 특정 배블에 리배블 생성
    - `DELETE /babbles/<id>/rebabbles`: 특정 배블의 리배블 삭제
- Like 관련 API
    - `GET /users/<id>/likes`: 특정 유저가 좋아요 누른 배블 목록 조회
    - `POST /babbles/<id>/likes`: 특정 배블에 좋아요 생성
    - `DELETE /babbles/<id>/likes`: 특정 배블의 좋아요 삭제
- Tag 관련 API
    - `GET /tags/<text>`: 특정 태그 목록 조회
- Notification 관련 API
    - `GET /users/notifications`: 로그인한 유저의 읽지 않은 알림 목록 조회
    - `POST /users/notifications`: 읽은 알람 처리
- Follower 관련 API
    - `POST /users/<id>/followers`: 특정 유저를 팔로잉
    - `DELETE /users/<id>/followers`: 특정 유저를 언팔로잉

## 4. 문제해결

1. 외부 의존도 제거
    - 오디오를 텍스트로 변환하고 변환된 텍스트에서 감정과 키워드를 추출하는 작업을 외부 api를 사용해서 개발했으나, 속도가 너무 느리고 외부 api가 많아지면 의존도가 높아지는 위험이 있다고 판단하여 공개된 인공지능을 사용하여 의존도를 낮췄습니다.
2. IsOwnerOrReadOnly 구현
    - 리퀘스트의 요청자가 모델의 유저와 다르면 읽기만 허용해주는 권한을 설정하고 싶었으나, 장고에서는 기본적으로 제공하지 않아 직접 만들었습니다.
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
            
3. import 오류 해결
    - whisper.py에서 외부라이브러리 import whisper가 안되는 오류가 발생했습니다. 파일 이름을 수정하니 해결되었습니다.
4. 빈 문자열로 저장
    - 문자열 기반 필드에 null=True 옵션을 넣었더니 빈 문자열이 아닌 None으로도 저장되는 오류가 발생해null=True를 지워서 해결했습니다.
5. 구조 개선과 캐시 적용
    - 처음엔 한 유저가 게시물을 작성하면 db에 저장되고 게시물을 조회할 때 한 유저가 팔로우하는 유저들을 전부 조회하고 그 유저들의 게시물을 가져오는 방식으로 만들었습니다. 그런데 읽기 작업이 굉장히 많은 SNS 특성상 이 구조가 좋지 못하다 생각해 트위터의 구조를 보고 캐시를 적용했습니다.
        - 캐시 적용 전
            
            ![noncache](https://user-images.githubusercontent.com/53591258/228713265-4b42ed54-0fc0-4da0-b722-f1d56b03a68a.png)
            
        - 캐시 적용 후
            
            ![cache](https://user-images.githubusercontent.com/53591258/228713305-a2d3bdf3-04b3-474e-9852-782df191e122.png)
            
6. 앱 라벨 적용
    - RuntimeError: Model class project.models.User doesn't declare an explicit app_label and isn't in an application in INSTALLED_APPS. 이라는 오류가 발생해 유저 모델에 다음 코드를 추가했습니다.
        - 코드
            
            ```python
            class User(models.Model):
                # fields and methods here
            
                class Meta:
                    app_label = 'your_app_label'
            ```
            
7. 마이그레이션 오류 해결
    - django.db.migrations.exceptions.InconsistentMigrationHistory: Migration admin.0001_initial is applied before its dependency users.0001_initial on database 'default'. 이라는 오류가 발생해 installed app에서 admin비활성화 후 마이그레이션 실행 후 다시 활성화 다시 마이그레이션했습니다.
8. N + 1 Problem 해결
    - 게시물 조회에서 N+1 문제가 발생했으나 select_related와 prefetch_related를 사용해 해결했습니다.
        - 문제 코드
            
            ```python
            babbles = Babble.objects.filter(
                    Q(user__in=user.self.all().values_list("following", flat=True)) | Q(user=user)
                ).order_by("-created")[start:end]
            ```
            
            | Type | Database | Reads | Writes | Totals | Duplicates |
            | --- | --- | --- | --- | --- | --- |
            | RESP | default | 44 | 0 | 44 | 41 |
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
            | Total queries: 5 in 0.0456s |  |  |  |  |  |
9. 테스트 코드 작성
    - 새로운 기능을 추가하면 제대로 구동이 되는지 화면상에서 하나하나 눌러보며 테스트를 하다가 너무 불편하고 비효율적이라 느껴 테스트코드를 작성하기 시작했습니다. 총 62개의 테스트 코드를 작성했습니다.
10. RESTful API 개선
    - 프로젝트를 완성한 후 README 파일에 기록할 API 설계를 작성하던 중, 기존의 API 설계가 RESTful한 원칙을 따르지 못하고 있음을 발견했습니다. 이를 개선하여 확장성이 높은 설계로 업데이트 하였습니다.

## 5. 프로젝트를 진행하면서 느낀점

1. 설계 문서의 필요성
    - 프로젝트 시작 전에 간략한 설계를 진행했지만, 체계적이지 않은 문서로 인해 개발 과정에 혼선이 발생했습니다. 이로 인해 API 설계의 결함을 발견하게 되었고, 문제를 해결하기 위해 많은 시간과 노력을 쏟아부어야 했습니다. 프로젝트 초기에 신속한 개발이 가능할지라도, 후반부에 발생하는 문제를 해결하는 데 드는 시간이 더 많아지기 때문에 완성도 있는 설계 문서의 필요성을 절감하게 되었습니다.
2. AI Model서빙을 위한 서버 구조
    - `음성 → 텍스트 → 감정분석` 의 작업에 인공지능을 사용합니다. 이 과정에서 많은 시간이 발생하고 이는 사용자의 불편으로 이어질 수 있다고 생각합니다. 이를 통해 인공지능을 효과적으로 사용하기 위한 서버의 설계는 무엇일지 궁금증이 생겼습니다.
3. 비지니스 로직의 분리
    - 트위터의 구조를 기반으로 개선 작업을 진행하면서, 비즈니스 로직이 복잡해지는 문제에 직면했습니다. 이에 대응하여 저는 utils.py라는 파일을 생성해 복잡한 로직을 분리했습니다. 결과적으로 views.py의 코드는 간결하고 읽기 쉬워졌으나, 해당 코드의 작동 원리를 확인하려면 파일 간 이동이 필요한 번거로움이 발생했습니다. 이 경험을 통해 비즈니스 로직을 더 효과적으로 분리하는 방법에 대한 고찰이 필요하다고 느꼈습니다.
4. 공식 문서의 중요성
    - 오류 발생 시 검색을 통해 다양한 해결 방법을 찾을 수 있습니다. 이 중에서 정확한 방법이 없을 수도 있습니다. 실제로 URL 구조를 개선하면서 router의 가능성과 제약 사항을 조사할 때, 많은 불필요한 정보 때문에 문제를 해결하지 못했습니다. 그러던 중 공식 문서를 참조하면 도움이 될 것 같다는 생각이 들어 찾아봤고, 그곳에서 다양한 router 예제를 발견해 문제를 쉽게 해결할 수 있었습니다. 이 경험을 통해 문제 발생 시 우선 공식 문서나 공식 깃허브의 이슈를 확인하는 것이 좋다고 깨달았습니다.
