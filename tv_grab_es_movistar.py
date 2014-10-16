#!/usr/bin/env python
# TO DO:
# - Fixing encoding and parsing issues
# - Adding tv_grab standard options
# - Using a temporary file to save user province, channels and epg days, so we save time in each execution

# Stardard tools
import sys
import os
import re
import logging

# Time handling
import time
import datetime
from datetime import timedelta

# XML
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment, ElementTree

from tva import TvaStream, TvaParser

logger = logging.getLogger('movistarxmltv')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('/home/pi/.hts/tvheadend/movistar.log')
fh.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

reload(sys)

SOCK_TIMEOUT = 5
MCAST_GRP_START = '239.0.2.129'
MCAST_PORT = 3937
MCAST_CHANNELS = '239.0.2.140'
FILE_XML = '/home/pi/.hts/tvheadend/tv_grab_es_movistar.xml'
FILE_M3U = '/home/pi/.hts/tvheadend/tv_grab_es_movistar.m3u'
FILE_LOG = '/home/pi/.hts/tvheadend/tv_grab_es_movistar.log'


# Andalucia 15
# Aragon    34
# Asturias  13
# Cantabria 29
# Castilla# la# Mancha  38
# Castilla# y# Leon 4
# Cataluna  1
# Comunidad# Valenciana 6
# Extremadura   32
# Galicia   24
# Islas# Baleares   10
# Islas# Canarias   37
# La# Rioja 31
# Madrid    19
# Murcia    12
# Navarra   35
# Pais# Vasco   36
PROVINCE = '19'
ENCODING_EPG = 'utf-8'
DECODING_EPG = 'latin1'
ENCODING_SYS = sys.getdefaultencoding()
#print "The default system encoding is : " + ENCODING_SYS
sys.setdefaultencoding(ENCODING_EPG)
#ENCODING_SYS = sys.getdefaultencoding()
#print "The system encoding has been set to : " + ENCODING_SYS


if len(sys.argv) > 1:
#    if str(sys.argv[1]) == "--description" or  str(sys.argv[1]) == "-d":
    print "Spain (Multicast Movistar - py)"
else:
    print "Usage: "+ sys.argv[0]+' [DAY NUMBER(0 today)]'
    exit()



# Main starts
# TO-DO: Adding 7th day for EPG

#print "Looking for the ip of your province"
#ipprovince = getxmlprovince(MCAST_CHANNELS,MCAST_PORT,PROVINCE)
now = datetime.datetime.now()
OBJ_XMLTV = ET.Element("tv" , {"date":now.strftime("%Y%m%d%H%M%S"),"source_info_url":"https://go.tv.movistar.es","source_info_name":"Grabber for internal multicast of MovistarTV","generator_info_name":"python-xml-parser","generator_info_url":"http://wiki.xmltv.org/index.php/XMLTVFormat"})
#OBJ_XMLTV = ET.Element("tv" , {"date":now.strftime("%Y%m%d%H%M%S")+" +0200"})

first_day = int(sys.argv[1])
last_day = int(sys.argv[2])

logger.info("Getting channels list")

channelsstream = TvaStream(MCAST_CHANNELS,MCAST_PORT)
channelsstream.getfiles()
xmlchannels = channelsstream.files()["2_0"]

channelparser = TvaParser(xmlchannels)
OBJ_XMLTV = channelparser.channels2xmltv(OBJ_XMLTV)

channelsm3u = channelparser.channels2m3u()
if os.path.isfile(FILE_M3U):
    os.remove(FILE_M3U)
fM3u = open(FILE_M3U, 'w+')
fM3u.write(channelsm3u)
fM3u.close

for day in range(first_day,last_day):
    i=int(day)+130
    grabbedDay = now + timedelta(days=int(day))
    logger.info("Reading day " +  grabbedDay.strftime("%d-%m-%Y") )
    epgstream = TvaStream('239.0.2.'+str(i),MCAST_PORT)

    epgstream.getfiles()
    for i in epgstream.files().keys():
    #    logger.info("Parsing "+i)
        epgparser = TvaParser(epgstream.files()[i])
        epgparser.parseepg(OBJ_XMLTV,channelparser.getchannelsdic())


# A standard grabber should print the xmltv file to the stdout
strFirstDay = now + timedelta(days=int(first_day))
strLastDay = now + timedelta(days=int(last_day))

ElementTree(OBJ_XMLTV).write(FILE_XML)
FILE_XML = '/home/pi/.hts/tvheadend/tv_grab_es_movistar_'+strFirstDay.strftime("%Y-%m-%d")+'_'+strLastDay.strftime("%Y-%m-%d")+'.xml'
ElementTree(OBJ_XMLTV).write(FILE_XML)
FILE_XML = '/home/pi/.hts/tvheadend/tv_grab_es_movistar.xml'
ElementTree(OBJ_XMLTV).write(FILE_XML)

grabbingDuration = datetime.datetime.now() - now

logger.info("Grabbed "+ str(len(OBJ_XMLTV.findall('channel'))) +" channels and "+str(len(OBJ_XMLTV.findall('programme')))+ " programmes in " + str(grabbingDuration))
logger.info(grabbingDuration)


exit()
