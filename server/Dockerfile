FROM rtsp/lighttpd:latest

RUN apk add --no-cache python3 sqlite

COPY lighttpd.conf /etc/lighttpd/lighttpd.conf
COPY entrypoint.sh /entrypoint.sh

RUN mkdir -p /opt/manhwa/cgi-bin
COPY last_page.py hide_chapter.py /opt/manhwa/cgi-bin/

RUN chmod 0755 /entrypoint.sh /opt/manhwa/cgi-bin/last_page.py /opt/manhwa/cgi-bin/hide_chapter.py

ENTRYPOINT ["/entrypoint.sh"]
