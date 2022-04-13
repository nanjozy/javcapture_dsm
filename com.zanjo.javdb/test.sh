/bin/bash loader.sh --type movie --lang enu --input "{\"title\":\"星星\"}" --limit 1
sudo -u nobody /var/packages/VideoStation/target/plugins/syno_plugin_tester/loader.sh --type movie --lang jpn --input "{\"title\":\"aki-012\"}" --limit 1 --path "/volume3/homes/zanjo/com.zanjo.javdb/loader.sh" --pluginid com.zanjo.javdb
tar --no-xattrs -cvf com.zanjo.javdb.tar com.zanjo.javdb

sudo -u nobody /bin/bash loader.sh --type movie --lang enu --input "{\"title\":\"AKI-012\"}" --limit 1

sudo -u nobody /usr/bin/python3 test.py --type movie --lang jpn --input "{\"title\":\"aki-012\"}" --limit 1 --path "/volume3/homes/zanjo/com.zanjo.javdb/loader.sh" --pluginid com.zanjo.javdb