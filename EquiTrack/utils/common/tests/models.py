from __future__ import absolute_import, division, print_function, unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.db import models

from utils.common.models.fields import CodedGenericRelation


class CodedGenericChild(models.Model):
    field = models.IntegerField()

    content_type = models.ForeignKey(ContentType)
    object_id = models.IntegerField()

    code = models.CharField(max_length=20, blank=True)


class Parent(models.Model):
    field = models.IntegerField()

    children1 = CodedGenericRelation(CodedGenericChild, code='children1')
    children2 = CodedGenericRelation(CodedGenericChild, code='children2')


class Child1(models.Model):
    field = models.IntegerField()

    parent = models.ForeignKey(Parent)