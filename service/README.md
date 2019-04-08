# install as a service

- Add sms_daemon.service in /etc/systemd/system
- Enable the service: sudo systemctl enable sms_daemon.service
- Start and stop the service: sudo systemctl start|stop sms_daemon.service
- Query status of the service: sudo systemctl status sms_daemon.service