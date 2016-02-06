FROM index.alauda.cn/toughstruct/tough-pypy:kiss
MAINTAINER jamiesun <jamiesun.net@gmail.com>

VOLUME [ "/var/toughtester" ]

ADD scripts/toughrun /usr/local/bin/toughrun
RUN chmod +x /usr/local/bin/toughrun
RUN /usr/local/bin/toughrun install

EXPOSE 8089
EXPOSE 3799/udp

CMD ["/usr/local/bin/supervisord","-c","/etc/supervisord.conf"]

