from flask import (
    abort,
    make_response,
    request,
    session,
)
import os, uuid

from functools import wraps
from models.user import User
from utils import log, copy_attrs

import redis

strict_redis = redis.StrictRedis(host='localhost', port=6379, db=0)

def interceptor(route_fn, response_maked):
    '''
    拦截器，用于检查响应路由的请求和响应

    route_fn: 路由函数
    response_maked: 表示路由函数是不是返回一个 response 实例
    '''

    @wraps(route_fn)
    def fn(*args, **kwargs):
        log(request.headers)

        # 设置 headers 允许跨域
        headers = {
            'Access-Control-Allow-Origin': request.headers.get('Origin'),
            'Access-Control-Allow-Headers': 'Content-Type,Content-Length,Authorization,\'Origin\',Accept,X-Requested-With',
            'Access-Control-Allow-Credentials': 'true',
        }

        response = route_fn(*args, **kwargs)
        if not response_maked:
            response = make_response(response)

        for k, v in headers.items():
            response.headers[k] = v
        return response

    return fn


def set_route(blueprint, *args, response_maked=False, **kwargs):
    """
    封装拦截器
    """

    def fn(route_fn):
        route_fn = interceptor(route_fn, response_maked)
        blueprint.route(*args, **kwargs)(route_fn)

    return fn


def processImg(file):
    '''
    处理上传图片
    '''
    # 用户可能通过文件名字访问的服务器内部的文件，也有可能写脚本
    # 需要对文件名字做处理
    # ../../root/.ssh/authorized_keys
    suffix = file.filename.split('.')[-1]
    filename = '{}.{}'.format(str(uuid.uuid4()), suffix)
    path = os.path.join('images', filename)
    file.save(path)

    return '/images/{}'.format(filename)


def same_user_required(model):

    def wrapper(route_fn):
        @wraps(route_fn)
        def fn(*args, **kwargs):
            log(args, kwargs)
            model_id = kwargs['id']
            uid = session.get('user_id', -1)
            
            u = User.one(id=uid)
            m = model.one(id=model_id)
            log('id', u, m)
            if u is None or m.user_id != uid:
                # 没有权限，返回 401
                abort(401)
            else:
                return route_fn(*args, **kwargs)

        return fn
    return wrapper


def xsrf_token_required(route_fn):
    '''
    通过比较客户端的 cookies 中的 token 跟请求数据中的 token 是否一致
    来判断是否是用户自己的操作
    '''

    @wraps(route_fn)
    def fn(*args, **kwargs):
        _xsrf = request.cookies.get('_xsrf')
        token = request.args.get('token')
        log(_xsrf, token)
        if _xsrf is not None and _xsrf == token:
            return route_fn(*args, **kwargs)
        else:
            # xsrf 不相等，说明不是用户操作
            abort(401)
    return fn


def login_required(route_fn):

    @wraps(route_fn)
    def fn(*args, **kwargs):
        uid = session.get('user_id', -1)
        u = User.one(id=uid)
        if u is None:
            abort(401)
        else:
            return route_fn(*args, **kwargs)
    return fn


def users_from_content(content):
    parts = content.split()
    users = []

    for p in parts:
        if p[0] == '@':
            name = p[1:]
            u = User.one(username=name)
            if u is not None:
                users.append(u)
    log('users:', users)
    return users


def get_user_data(id, attrs=['id', 'username', 'avatar']):
    u = User.one(id=id)
    if u is None:
        u = User.guest()
    d = copy_attrs(attrs, u)
    return d
