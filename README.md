# cookbook
https://django-orm-cookbook-ko.readthedocs.io/en/latest/

# poetry
1. brew install poetry
2. poetry init
3. poetry add django
4. poetry run python manage.py runserver

# details

### 1. 장고 ORM이 실행하는 실제 SQL 질의문을 확인할 수 있나요?

```python
queryset = User.objects.filter(pk=[1,2,3])
print(str(queryset.query))  # str(queryset.query) SQL 질의문 확인

filter(years_ago__gt=5)  
"""
lt: 작은  # WHERE "events_event"."years_ago" < 5'
lte: 작거나 같은  # WHERE "events_event"."years_ago" <= 5'
gt: 큰  # WHERE "events_event"."years_ago" > 5'
gte: 크거나 같은  # WHERE "events_event"."years_ago" >= 5'
"""
all().order_by('-id')[:10]  # ORDER BY "events_event"."id" DESC LIMIT 10
```

### 2. OR 연산으로 일부 조건을 하나라도 만족하는 항목을 구하려면 어떻게 하나요?

```python
# SELECT username, first_name, last_name, email FROM auth_user WHERE first_name LIKE 'R%' OR last_name LIKE 'D%';

# 1. 비효율적
# queryset = User.objects.filter(
#     first_name__startswith='R'
# ) | User.objects.filter(
#     last_name__startswith='D'
# )

# 2.
from django.db.models import Q
queryset = User.objects.filter(Q(first_name__startswith='R') | Q(last_name__startswith='D'))

```

### 3. AND 연산으로 여러 조건을 모두 만족하는 항목을 구하려면 어떻게 하나요?

```python
# SELECT username, first_name, last_name, email FROM auth_user WHERE first_name LIKE 'R%' AND last_name LIKE 'D%';
# 장고 쿼리셋의 filter 메서드에서 여러 조건을 결합하는 방법은 기본적으로 AND 방식이다.
queryset1 = User.objects.filter(first_name__startswith='R', last_name__startswith='D')
# queryset2 = User.objects.filter(first_name__startswith='R') & User.objects.filter(last_name__startswith='D') 비효율적
queryset3 = User.objects.filter(Q(first_name__startswith='R') & Q(last_name__startswith='D'))

str(queryset1.query) == str(queryset2.query) == str(queryset3.query)  # True
```

### 4. NOT 연산으로 조건을 부정하려면 어떻게 하나요?

```python
# SELECT id, username, first_name, last_name, email FROM auth_user WHERE NOT id < 5;
## exclude()
queryset = User.objects.exclude(id=lt=5)
## filter()
queryset = User.objects.filter(~Q(id__lt=5))  # ~Q 부정
```

### 5. 동일한 모델 또는 서로 다른 모델에서 구한 쿼리셋들을 합할 수 있나요?

- UNION (합집합)
  - 중복된 영역을 제외하고 하나로 합치는 연산

```python
# 여러 개의 집합을 합할 때 UNION 연산을 이용합니다.
# 장고 ORM 에서 UNION 메서드를 이용해 쿼리셋을 합할 수 있습니다.
# 합 하려는 쿼리셋의 모델이 서로 다른 경우, 
# 각 쿼리셋에 포함된 필드와 데이터 유형이 서로 맞아야 합니다.
queryset1 = User.objects.filter(id__gte=5)
queryset2 = User.objects.filter(id__lte=9)

# 쿼리셋의 필드와 데이터 유형이 서로 일치할 때만 실행할 수 있습니다.
# Here 모델과 Villain 모델은 둘 다 name, gender 필드를 갖고 있습니다.
# values_list 를 이용해 공통된 필드만 가져온 뒤 UNION을 수행할 수 있습니다.
queryset1.union(queryset2)
queryset2.union(queryset1)

Here.objects.all().values_list(
    "name", "gender"
).union(
    Villain.objects.all().values_list(
        "name", "gender"
    )
)
```

### 6. 필요한 열만 골라 조회하려면 어떻게 하나요?

- only() vs values()
  - only() 메서드의 경우 id 필드를 가져온다.

- values vs values_list
  - values 는 쿼리셋의 값을 딕셔너리 형태로 반환한다.
  - values_list 는 쿼리셋의 값을 튜플 형태로 만든다.

```python
Post.objects.filter(id__lt=8).values('title')
# <QuerySet [{'title': 'post #1'}, {'title': 'title #1'}, {'title': 'title #2'}]>
Post.objects.filter(id__lt=8).values_list('title')
# <QuerySet [{'title': 'post #1'}, {'title': 'title #1'}, {'title': 'title #2'}]>
```

1. ORM 사용하면 매우 편리하게 DB를 사용할 수 있어서 좋지만 떄로는 비합리적으로 동작할 때가 있어 대용량 데이터를 다룰 때 문제가 될 수 있다.
2. values() 와 values_list() 는 ORM 쿼리 최적화의 방법 중 하나로서 필요한 필드의 값만 가져올 수 있고, 따라서 DB에 부하를 줄일 수 있다.

```python
# values
User.objects.filter(
    first_name__startswith='R'
).values('first_name', 'last_name')  # SELECT "auth_user"."first_name", "auth_user"."last_name" FROM "auth_user" WHERE "auth_user"."first_name"::text LIKE R%
# only 메서드
queryset = User.objects.filter(
    first_name__startswith='R'
).only('first_name', 'last_name')  # SELECT "auth_user"."id", "auth_user"."first_name", "auth_user"."last_name" FROM "auth_user" WHERE "auth_user"."first_name"::text LIKE R%
```

```python
# ---
# 6. 필요한 열만 골라 조회하려면 어떻게 하나요?
## 쿼리셋의 values 메서드와 values_list 메서드
User.objects.filter(
    first_name__startswith='R'
).values('first_name', 'last_name')  # SELECT "auth_user"."first_name", "auth_user"."last_name" FROM "auth_user" WHERE "auth_user"."first_name"::text LIKE R%
## only 메서드
queryset = User.objects.filter(
    first_name__startswith='R'
).only('first_name', 'last_name')  # SELECT "auth_user"."id", "auth_user"."first_name", "auth_user"."last_name" FROM "auth_user" WHERE "auth_user"."first_name"::text LIKE R%
## only 메서드가 values 메서드와 다른 점은 id 필드를 가져온다는 점
# ---
# 7. 장고에서 서브쿼리(subquery) 식을 사용할 수 있나요?
## 서브쿼리, 질의문 내의 하위 질의
## 내부 쿼리의 결과를 기반으로 데이터를 필터링, 검색 또는 조작 하는 데 자주 사용되는 다른 쿼리 내에 포함된 쿼리 입니다.
### https://velog.io/@engineer_km/Django-ORM-QuerySet%EA%B5%AC%EC%A1%B0%EC%99%80-%EC%9B%90%EB%A6%AC-%EA%B7%B8%EB%A6%AC%EA%B3%A0-%EC%B5%9C%EC%A0%81%ED%99%94%EC%A0%84%EB%9E%B5-PyCon-Korea-2020-%EB%B0%9C%ED%91%9C-%EC%A0%95%EB%A6%AC
from django.db.models import Subquery, OuterRef


class Category(models.Model):
    name = models.CharField(max_length=100)


class Hero(models.Model):
    # ...
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    benevolence_factor = models.PositiveSmallIntegerField(
        help_text="How benevolent this hero is?",
        default=50
    )

hero_qs = Hero.objects.filter(
    category=OuterRef("pk")  # 서브쿼리; 메인쿼리와 조인할 컬럼을 OuterRef 메소드를 지정한다.
).order_by("-benevolence_factor")
Category.objects.all().annotate(  # annotate: 엑셀에서 계산용 컬럼을 하나 추가하는 것과 같다. / aggregate: 액셀에서 특정 컬럼 전체를 대상으로 계산하는 것과 같다. (합, 평균, 개수 등)
    most_benevolent_hero=Subquery(  # most_.. 별칭
        hero_qs.values('name')[:1]  # 첫 번쨰 행의 'name' 을 구한다.
    )
)
# ---
# 8. 필드의 값을 서로 비교하여 항목을 선택할 수 있나요?
from django.db.models.functions import Substr
User.objects.filter(last_name=F("first_name"))  # 이름과 성이 동일한 사용자 찾기 / F("first_name") User Model 에 first_name을 가져온다.
## F 는 모델의 필드, 파이썬 메모리로 데이터를 가져오는 것이 아니라, 그 연산에 해당하는 쿼리를 만들어낸다.
user = User.objects.get(name='Tim')
user.age = F('age') + 1
user.save()
## 하지만 굳이 인스턴스를 만들어서 파이썬에서 할 필요가 없다.
User.objects.update(age=F('age') + 1)
##* F 객체는 annotate 메서드로 계산해 둔 필드를 가리킬 때도 사용할 수 있습니다.
# 이름의 첫 글자와 성의 첫 글자가 동일한 사용자를 구하고 싶다면
## Substr(expression, pos, length=None, **extra)
User.objects.annotate(first=Substr("first_name", 1, 1), last=Substr("last_name", 1, 1)).filter(first=F("last"))
## F 객체에서 __get, __lt 등의 룩업을 적용하는 것 또한 가능합니다.
## F() 의 장점
### 1. 데이터베이스에서 쿼리 처리르 통해 성능을 높일 수 있다.
### 2. 작업에 필요한 쿼리를 줄일 수 있다.
### 3. Race Condition 문제를 회피
### 장고는 데이터베이스 정보를 메모리로 가져와 처리한다. 만약 여러 요청이 동시에 하나의 객체로 접근 한다면 문제가 발생할 것이다.
# ---
# 9. FileField 에 파일이 들어있지 않은 행은 어떻게 구할 수 있나요?
## FileField 와 ImageField 는 파일과 이미지 파일의 경로를 저장합니다. 데이터베이스 수준에서는 모두 CharField 와 동일한 방식으로 저장합니다.
no_files_objects = MyModel.objects.filter(
    Q(file='')|Q(file=None)
)
# ---
# 10. 두 모델을 결합(JOIN) 하려면 어떻게 하나요?
## SQL 에서는 JOIN 문을 이용해 동일한 값을 가진 열을 기준으로 두 표를 결합할 수 있습니다. 결합 연산은 여러 가지 방법으로 수행할 수 있습니다.
## JOIN 여러 개의 테이블을 연결해준다.
### INNER JOIN
a1 = Article.objects.select_related('reporter')  
# select_related 는 ForeignKey(1:N) or OneToOne / 단일 SQL 쿼리로 관련 객체를 가져옵니다. 이 방법은 쿼리 성능이 향상될 수 있지만, 많은 데이터가 조인되면 비효율적일 수 있습니다.
# prefetch_related 는 ForeignKey or OneToOne or ManyToMany or OneToMany / SQL 쿼리로 관련 객체를 가져옵니다. 이 방법은 메모리 사용량이 증가할 수 있지만, 쿼리 수가 줄어들어 성능이 향상될 수 있습니다. 
"""
SELECT "events_article"."id", "events_article"."headline", "events_article"."pub_date", "events_article"."reporter_id", "events_article"."slug", "auth_user"."id", "auth_user"."password", "auth_user"."last_login", "auth_user"."is_superuser", "auth_user"."username", "auth_user"."first_name", "auth_user"."last_name", "auth_user"."email", "auth_user"."is_staff", "auth_user"."is_active", "auth_user"."date_joined" FROM "events_article" INNER JOIN "auth_user" ON ("events_article"."reporter_id" = "auth_user"."id") ORDER BY "events_article"."headline" AS
"""
a2 = Article.objects.filter(reporter__username='John')

class Article(models.Model):
    id = models.AutoField(primary_key=True)
    headline = models.CharField(max_length=100)
    pub_date = models.DateField()
    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reporter'
    )
# ---
# 11. 두 번째로 큰 항목은 어떻게 구하죠?
## N 번째 항목을 구하는 메서드는 제공되지 않습니다. 그 대신, 파이썬의 인덱싱 연산을 이용할 수 있습니다.
user = User.objects.order_by('-last_login')[1]  # 내림차순 두 번째 데이터 / 쿼리셋에 인덱스 연산을 지시할 때 장고 ORM 은 데이터베이스에서 전체 데이터를 가져온 뒤 인덱싱을 하는 것이 아니라 LIMIT, OFFSET SQL 구문을 이용해 필요한 데이터만 읽어 옵니다.
user = User.objects.order_by('-last_login')[2]  # 내림차순 세 번째 데이터
"""
SELECT "auth_user"."id",
       "auth_user"."password",
       "auth_user"."last_login",
       "auth_user"."is_superuser",
       "auth_user"."username",
       "auth_user"."first_name",
       "auth_user"."last_name",
       "auth_user"."email",
       "auth_user"."is_staff",
       "auth_user"."is_active",
       "auth_user"."date_joined"
FROM "auth_user"
ORDER BY "auth_user"."last_login" DESC
LIMIT 1  # 제한 == [2]
OFFSET 2  # 조회를 시작할 기준점 [0, 1, `2`]
"""
# ---
# 12. 특정 열의 값이 동일한 항목은 어떻게 찾나요?
deplicates = User.objects.values('first_name').annotate(
        name_count=Count('first_name')).filter(name_count__gt=1) # <QuerySet [{'first_name': 'Tim', 'name_count': 2}]>

records = User.objects.filter(first_name__in=[item['first_name'] for item in deplicates])
print([item.id for item in records])  # [3, 4]
# ---
# 13. 쿼리셋에서 고유한 필드 값을 가진 항목은 어떻게 구하나요?
## 값을 필터링
distinct = User.objects.values(
    'first_name'
).annotate(
    name_count=Count('first_name')
).filter(name_count=1)
## 출력
records = User.objects.filter(first_name__in=[item['first_name'] for item in distinct])
## distinct 중복 레코드 제거
### !WHAT! PostgreSQL 에서만 가능
User.objects.distinct("first_name").all()
# ---
# 14. Q 객체를 이용해 복잡한 질의를 수행하는 방법은 무엇인가요?
## Q 객체를 통해 OR 연산, AND 연산, NOT 연산을 수행했다. Q 객체를 이용하면 SQL 질의문의 `WHERE(조건)` 절에 해당하는 기능을 온전히 활용할 수 있습니다.
from django.db.models import Q
queryset_or = User.objects.filter(
    Q(first_name__startswith='R') | Q(last_name__startswith='D')  # OR
)

queryset_and = User.objects.filter(
    Q(first_name__startswith='R') & Q(last_name__startswith='D')  # AND
)

queryset_not = User.objects.filter(
    Q(first_name__startswith='R') & ~Q(last_name__startswith='Z')  # NOT
)
# ---
# 15. 기록된 항목의 집계를 구할 수 있나요?
## 장고 ORM 을 이용해 항목을 생성, 조회, 갱신, 삭제할 수 있지만, 때로는 항목들의 집계값을 구하고 싶을 때가 있습니다. 장고 ORM 에는 SQL의 일반적인 집계 기능을 수행하는 Max, Min, Avg, Sum 등의 함수가 있습니다.
from django.db.models import Avg, Max, Min, Sum, Count
User.objects.all().aggregate(Avg('id'))
# {'id__avg': 7.571428571428571}
>>> User.objects.all().aggregate(Max('id'))
# {'id__max': 15}
>>> User.objects.all().aggregate(Min('id'))
# {'id__min': 1}
>>> User.objects.all().aggregate(Sum('id'))
# {'id__sum': 106}
# ---
# 16. 항목을 무작위로 뽑고 싶습니다. 효율적인 방법이 있을까요?
class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

## 1. order_by 메서드로 항목들을 정렬할 때, 정렬 기준을 '무작위'로 지정하는 것 입니다. 데이터를 무작위로 정렬하여 첫 번째 항목을 가져오면 무작위 항목을 구할 수 있습니다.
def get_random():
    return Category.objects.order_by("?").first()
### 주의: 사용하는 데이터베이스 시스템에 따라 order_by('?') 의 실행 비용이 비싸다고 성능이 느릴 수 있습니다.

## 2. 전체 표를 정렬하는 대신 저장된 항목의 마지막 ID를 이용하는 것 입니다. 표에서 ID의 최대값을 구하고, 1과 마지막 ID 사이의 난수를 하나 생성합니다.
from django.db.models import Max
from entities.models import Category
import random

def get_random2():
    max_id = Category.objects.all().aggrgate(max_id=Max("id"))['max_id']
    pk = random.randint(1, max_id)
    return Category.objects.get(pk=pk)
### 이 방법은 항목을 삭제하거나 해서 ID 가 중간에 비어있는 경우에는 쓸 수 없습니다. 그런 경우에는 유효한 값이 나올 때 까지 반복하도록 하면 됩니다.

## 3. 위의 함수를 수정
def get_random3():
    max_id = Cateogry.objects.all().aggregate(max_id=Max("id"))['max_id']
    while True:
        pk = random.randint(1, max_id)
        category = Category.objects.filter(pk=pk).first()
        if category:
            return category
### 삭제된 항목이 많지 않다면 무한반복 구문은 금방 종료될 것 입니다.
In [14]: timeit.timeit(get_random3, number=100)
Out[14]: 0.20055226399563253

In [15]: timeit.timeit(get_random, number=100)
Out[15]: 56.92513192095794
### get_random3 이 get_random 보다 283배 빠르게 실행 되었습니다.
### get_random 은 언제나 이용할 수 있는 반면에, get_random3 의 방법은 장고의 기본 ID 생성 방식을 재정의한 경우나 삭제된 항목이 너무 많을 때에는 사용하기가 어려울 수 있습니다.
```
