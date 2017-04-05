#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from flask import request, g

from planet.extensions import db
from planet.utils.permissions import auth
from planet.utils.schema import render_schema, render_error
from planet.post import post_api
from planet.post.schemas import PostSchema
from planet.post.models import get_all_posts, get_post
from planet.post.permissions import (post_list_perm, post_show_perm,
                                     post_create_perm, post_update_perm,
                                     post_destory_perm)


@post_api.route('', methods=['GET'])
@auth.require(401)
@post_list_perm.require(403)
def index():
    page = int(request.values.get('p', 1))
    limit = int(request.values.get('limit', 20))
    posts = get_all_posts(page=page, limit=limit)
    return render_schema(posts, PostSchema())


@post_api.route('/<id_or_slug>', methods=['GET'])
@auth.require(401)
@post_show_perm.require(403)
def show(id_or_slug):
    post = get_post(id_or_slug)
    return render_schema(post, PostSchema())


@post_api.route('', methods=['POST'])
@auth.require(401)
@post_create_perm.require(403)
def create():
    payload = request.get_json()
    if not payload:
        return render_error(20001, 'No input data provided')
    post_schema = PostSchema(exclude=('id', 'created_at', 'updated_at'))
    post_data, errors = post_schema.load(payload)
    if errors:
        return render_error(20001, errors, 422)
    post_data.author = g.user
    post_data.updated_by = g.user.id
    if post_data.status == 'published':
        post_data.published_at = datetime.utcnow
        post_data.published_by = g.user.id
    db.session.add(post_data)
    db.session.commit()
    return render_schema(post_data, PostSchema())


@post_api.route('/<id>', methods=['PUT'])
@auth.require(401)
@post_update_perm.require(403)
def update(id):
    post = get_post(id)
    playload = request.get_json()
    if not playload:
        return render_error(20001, 'No input data provided')
    post_schema = PostSchema(exclude=('image', 'created_at', 'updated_at',
                                      'author'))
    post_data, errors = post_schema.load(playload)
    if errors:
        return render_error(20001, errors, 422)
    post_data.updated_by = g.user.id
    if post.status != 'published' and post_data.status == 'published':
        post_data.published_at = datetime.utcnow
        post_data.published_by = g.user.id
    db.session.add(post_data)
    db.session.commit()
    return render_schema(post_data, PostSchema())


@post_api.route('/<id>', methods=['DELETE'])
@auth.require(401)
@post_destory_perm.require(403)
def destory(id):
    post = get_post(id)
    db.session.delete(post)
    db.session.commit()

    message = {'code': 10000, 'message': 'success'}

    return render_schema(message)
