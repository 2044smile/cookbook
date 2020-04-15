import uuid

from django.db import models
from django.utils.text import slugify  # slug를 만들기 위한 모듈
from entities.models import Hero, Villain
from django.contrib.auth.models import User


class Epic(models.Model):
    name = models.CharField(max_length=255)
    participating_heroes = models.ManyToManyField(Hero)
    participating_villains = models.ManyToManyField(Villain)


class Event(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False  # 수정 가능 유무
        # ex) DateTimeField의 auto_now_add 속성이 True로 설정되면 editable 속성이 자동으로
        # False 로 설정되기 때문에 editable 속성을 True로 변경해주면 디테일 화면에서 확인 및 수정이 가능해진다.
    )
    epic = models.ForeignKey(Epic, on_delete=models.CASCADE)
    details = models.TextField()
    years_ago = models.PositiveIntegerField()


class EventHero(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    hero = models.ForeignKey(Hero, on_delete=models.CASCADE)
    is_primary = models.BooleanField()


class UserParent(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    father_name = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)


class Article(models.Model):
    headline = models.CharField(max_length=100)
    pub_date = models.DateField()
    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reporter'
    )
    slug = models.SlugField()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.headline)
        super(Article, self).save(*args, **kwargs)

    def __str__(self):
        return self.headline

    class Meta:
        ordering = ('headline',)


class TempUser(models.Model):
    first_name = models.CharField(max_length=100)

    class Meta:
        managed = False  # 해당 모델은 자동으로 테이블을 생성하지 않게 된다.
        db_table = "temp_user"


class ColumnName(models.Model):
    a = models.CharField(
        max_length=40,
        db_column='column1'
    )
    column2 = models.CharField(max_length=50)

    def __str__(self):
        return self.a
