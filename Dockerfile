#docker version 18.03.1 ce
FROM python:3.6
LABEL maintainer="nico" email="jennei@hotmail.com" qq="303288346"
ENV TZ "Asia/Shanghai"
RUN mkdir /MyBlog\
    && mkdir -p /etc/uwsgi/vassals\
    && mkdir -p /etc/supervisor/conf.d\
    && mkdir -p /var/log/supervisor/
WORKDIR /MyBlog
ADD . /MyBlog/
RUN pip install -r requirements.txt -i https://pypi.douban.com/simple/\
    && pip install git+https://github.com/Supervisor/supervisor/
COPY tools/uwsgi/vassals/myblog_uwsgi.ini /etc/uwsgi/vassals/
COPY tools/supervisor/conf.d/myblog_uwsgi_supervisor.conf /etc/supervisor/conf.d/
COPY tools/supervisor/conf.d/myblog_celery_beat_supervisor.conf /etc/supervisor/conf.d/
COPY tools/supervisor/conf.d/myblog_celery_worker_supervisor.conf /etc/supervisor/conf.d/
COPY tools/supervisor/supervisord.conf /etc/supervisor/
ENTRYPOINT ["supervisord", "-c", "/etc/supervisor/supervisord.conf", "-n"]
EXPOSE 8000