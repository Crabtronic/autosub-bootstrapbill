#
# Autosub Addic7ed.py - https://code.google.com/p/autosub-bootstrapbill/
#
# The Addic7ed method specific module
#

import re
import library.requests as requests
from bs4 import BeautifulSoup
import time

import autosub
import autosub.Helpers
import autosub.Tvdb

from itertools import product


import logging

log = logging.getLogger('thelogger')

#Every part of the file_info got a list with regex. The first item in this list should be the standardnaming
#The second (and following) regex contains nonstandard naming (either typo's or other renaming tools (like sickbeard)) 
#Nonstandard naming should be renamed using the syn dictionary. 

source = [re.compile("(ahdtv|hdtv|web[. _-]*dl|bluray|dvdrip|webrip)", re.IGNORECASE),
          re.compile("(tv|dvd|bdrip|web)", re.IGNORECASE)]

#A dictionary containing as keys, the nonstandard naming. Followed by there standard naming.
#Very important!!! Should be unicode and all LOWERCASE!!!
source_syn = {u'tv' : u'hdtv',
              u'ahdtv' : u'hdtv',
              u'dvd' : u'dvdrip',
              u'bdrip': u'bluray',
              u'webdl' : u'web-dl',
              u'web' : u'web-dl'}


quality = [re.compile("(1080p|720p|480p)" , re.IGNORECASE), 
           re.compile("(1080[i]*|720|480|HD|SD)", re.IGNORECASE)]

quality_syn = {u'1080' : u'1080p',
               u'1080i' : u'1080p',
               u'720' : u'720p',
               u'480p' : u'sd',
               u'480' : u'sd', 
               u'hd': u'720p'}
               
codec = [re.compile("([xh]*264|xvid|dvix)" , re.IGNORECASE)]

#Note: x264 is the opensource implementation of h264.
codec_syn = {u'x264' : u'h264',
               u'264' : u'h264'}

#The following 2 variables create the regex used for guessing the releasegrp. Functions should not call them!
_releasegrps = ['0TV',
               '2HD',
               'ASAP',
               'aAF',
               'AFG',
               'AVS',
               'BAJSKORV',
               'BiA',
               'BS',
               'BTN',
               'BWB',
               'CLUE',
               'CP',
               'COMPULSiON',
               'CtrlHD',
               'CTU',
               'DEMAND',
               'DIMENSION',
               'DNR',
               'EbP',
               'ECI',
               'EVOLVE',
               'FEVER',
               'FOV',
               'FQM',
               'FUM',
               'GFY',
               'GreenBlade',
               'HoodBag',
               'HAGGiS',
               'hV',
               'HWD',
               'IMMERSE',
               'KiNGS',
               'KILLERS'
               'KYER',
               'LFF',
               'LOL',
               'LP',
               'MMI',
               'MOMENTUM',
               'mSD',
               'NBS',
               'NFHD',
               'NFT',
               'NIN',
               'nodlabs',
               'NoTV',
               'NTb',
               'OOO',
               'ORENJi',
               'ORPHEUS',
               'PCSYNDICATE',
               'P0W4',
               'P0W4HD',
               'playXD',
               'POD',
               'RANDi',
               'REWARD',
               'ROVERS',
               'RRH',
               'SAiNTS',
               'SAPHiRE',
               'SCT',
               'SiNNERS',
               'SkyM',
               'SLOMO',
               'sozin',
               'sundox',
               'TjHD',
               'TOPAZ', 
               'TLA',
               'TOKUS',
               'T00NG0D',
               'TVSMASH',
               'VASKITTU',
               'UP',
               'XOR',
               'XS',
               'YFN']

'''
_releasegrpsHD = ['DIMENSION',
                  'IMMERSE',
                  'ORENJi',
                  'EVOLVE',
                  'CTU',
                  'KILLERS',
                  '2HD',
                  'MOMENTUM']

_rlsgroupsSD = ['LOL',
                'ASAP',
                'FQM',
                'XOR',
                'NoTV',
                'FoV',
                'FEVER',
                'AVS',
                'COMPULSiON']

_rlsgroups_xvid = ['AFG']

_rlsgroups_h264 = ['TLA',
                  'BiA',
                  'BAJSKOR']

_rlsgroupsWebdl = ['YFN',
                   'FUM',
                   'BS',
                   'ECI',
                   'NTb',
                   'CtrlHD',
                   'NFHD',
                   'KiNGS',
                   'POD',
                   'TVSmash'
                   'HWD'
                   'PCSYNDICATE']
'''


_releasegrp_pre = '(' + '|'.join(_releasegrps) + ')'

releasegrp = [re.compile(_releasegrp_pre, re.IGNORECASE)]

rlsgroupsHD = re.compile("(DIMENSION|IMMERSE|ORENJi|EVOLVE|CTU|KILLERS|2HD|MOMENTUM)" , re.IGNORECASE)
rlsgroupsSD = re.compile("(LOL|ASAP|FQM|XOR|NoTV|FoV|FEVER|AVS|COMPULSiON)" , re.IGNORECASE)
rlsgroups_xvid = re.compile("(AFG)" , re.IGNORECASE)
rlsgroups_h264 = re.compile("(TLA|BiA|BAJSKORV)" , re.IGNORECASE)        
rlsgroupsWebdl = re.compile("(YFN|FUM|BS|ECI|NTb|CtrlHD|NFHD|KiNGS|POD|TVSmash|HWD|PCSYNDICATE)" , re.IGNORECASE)


def _returnHits(regex, version_info):
    # Should have been filter out beforehand
    results=[]
    if not version_info:
        results.append(-1)        
        return results
    
    for reg in regex:
        results = re.findall(reg, version_info)
        if results:
            results = [x.lower() for x in results]
            results = [re.sub("[. _-]", "-", x) for x in results]
            break
    return results
        
                    
def _checkSynonyms(synonyms, results):
    for index, result in enumerate(results):
        if result in synonyms.keys() and synonyms[result]:
            results[index] = synonyms[result].lower()
        else: continue
    return results


def _getSource(file_info):
    results = _checkSynonyms(source_syn,
                            _returnHits(source, file_info))
    return results

def _getQuality(file_info, HD):
    results = _checkSynonyms(quality_syn,
                            _returnHits(quality, file_info))
    '''
    This can cause conflicts with releasegroups
    Leave it out and see what happens
    if not results:
        # CheckBOX HD on a7
        if HD:
            results.append(u'720p')
    '''
    return results

def _getCodec(file_info):
    results = _checkSynonyms(codec_syn,
                            _returnHits(codec, file_info))
    
    return results

def _getReleasegrp(file_info):
    results = _returnHits(releasegrp, file_info)
    
    return results


def _ParseVersionInfo(version_info, HD):
    # Here the information in the a7 version columns get grouped 
    # Either source, quality, codec or releasegroup
    
    sourceList = _getSource(version_info)
    qualityList = _getQuality(version_info, HD)
    codecList = _getCodec(version_info)
    releasegroupList = _getReleasegrp(version_info)
    
    parametersList = [sourceList, qualityList, codecList, releasegroupList]   
    return parametersList

    
def _checkIfParseable(parametersList):
    for index,parameter in enumerate(parametersList):
        if len(parameter) > 1:
            tempLists = parametersList[:]
            tempLists.pop(index)
            for tempList in tempLists:
                if len(tempList) > 1:
                    return True
    return False


def _checkConflicts(versionDicts):
# Check if data is consistent in the dict
# If inconsistent, remove particalr dict
    toDelete = []
    for index, versionDict in enumerate(versionDicts):
        source = versionDict['source']
        quality = versionDict['quality']
        codec = versionDict['codec']
        releasegroup = versionDict['releasegrp']
        
        # The following combinations are inconsistent
        
        # Based on quality
        if quality == u'1080p':
            if source == u'hdtv':
                toDelete.append(index)
                continue
    
        # Based on source
        if source == u'web-dl':
            if codec == u'xvid':
                toDelete.append(index)
                continue
        
        elif source == u'hdtv':
            if quality == u'1080p':
                toDelete.append(index)
                continue

        # Based on releasegroup
        if releasegroup:
            if re.match(rlsgroupsHD, releasegroup) or \
                re.match(rlsgroupsSD, releasegroup) or \
                re.match(rlsgroups_h264, releasegroup) or \
                re.match(rlsgroups_xvid, releasegroup):
                if source == u'web-dl':
                    toDelete.append(index)
                    continue
            if re.match(rlsgroupsHD, releasegroup) or \
                re.match(rlsgroups_h264, releasegroup):
                if codec == u'xvid':
                    toDelete.append(index)
                    continue
            if re.match(rlsgroupsHD, releasegroup):
                if quality == u'sd':
                    toDelete.append(index)
                    continue
            if re.match(rlsgroups_xvid, releasegroup):
                if codec == u'h264':
                    toDelete.append(index)
                    continue
            if re.match(rlsgroupsSD, releasegroup):
                if quality == u'720p' or quality == u'1080p':
                    toDelete.append(index)
                    continue
    
    # Delete duplicate indices
    toDelete = sorted(set(toDelete))    
    i = len(toDelete) -1
    
    while i>=0:
        versionDicts.pop(toDelete[i])
        i=i-1
    return versionDicts   

def _addInfo(versionDicts):
    # assume missing codec is x264, error prone!
    for index, versionDict in enumerate(versionDicts):
        source = versionDict['source']
        quality = versionDict['quality']
        codec = versionDict['codec']
        releasegroup = versionDict['releasegrp']
    
        # Based on quality
        if quality == u'1080p':
            if not source:
                versionDicts[index]['source'] = u'web-dl'    
    
        # Based on source
        if any(source == x for x in (u'web-dl', u'hdtv', u'bluray')):
            if not codec:
                versionDicts[index]['codec'] = u'h264'
        if source == u'web-dl':
            # default quality for WEB-DLs is 720p
            if not quality:
                versionDicts[index]['quality'] = u'720p'

        # Based on specific Releasegroups  
        if releasegroup:  
            if re.match(rlsgroupsHD, releasegroup) or \
                re.match(rlsgroupsSD, releasegroup) or \
                re.match(rlsgroups_h264, releasegroup) or \
                re.match(rlsgroupsWebdl, releasegroup):
                if not codec:
                    versionDicts[index]['codec'] = u'h264'
            if re.match(rlsgroups_xvid, releasegroup):
                if not codec:
                    versionDicts[index]['codec'] = u'xvid'
            if re.match(rlsgroupsHD, releasegroup) or \
                re.match(rlsgroupsSD, releasegroup) or \
                re.match(rlsgroups_h264, releasegroup) or \
                re.match(rlsgroups_xvid, releasegroup):
                if not source:
                    versionDicts[index]['source'] = u'hdtv'  
            if re.match(rlsgroupsWebdl, releasegroup):
                if not source:
                    versionDicts[index]['source'] = u'web-dl'
            if re.match(rlsgroupsHD, releasegroup):
                if not quality:
                    versionDicts[index]['quality'] = u'720p'
            if re.match(rlsgroupsSD, releasegroup):
                if not quality:
                    versionDicts[index]['quality'] = u'sd'

    return versionDicts


def _MakeTwinRelease(originalDict):
    # This modules creates the SD/HD counterpart for releases with specific releasegroups
    
    rlsgroup = originalDict['releasegrp']
    qual = originalDict['quality']
    source = originalDict['source']
    
    rlsSwitchDict = {u'dimension' : u'lol', u'lol': u'dimension',
                     u'immerse': u'asap', u'asap' : u'immerse',
                     u'2hd' : u'2hd', u'bia' : u'bia', u'fov' : u'fov'}
    qualSwitchDict_hdtv = {u'sd' : u'720p', u'720p' : u'sd'}
    qualSwitchDict_webdl =  {u'1080p' : u'720p', u'720p' : u'1080p'}
    
    # DIMENSION <> LOL
    # IMMERSE <> ASAP
    # 2HD <> 2HD 720p
    # BiA <> BiA 720p
    # FoV <> FoV 720p
    twinDict = originalDict.copy()
    if rlsgroup in rlsSwitchDict.keys():
        twinDict['releasegrp'] = rlsSwitchDict[rlsgroup]
        twinDict['quality'] = qualSwitchDict_hdtv[qual]
    
    # WEB-DLs 720p and 1080p are always synced
    if source == 'web-dl' and qual in qualSwitchDict_webdl.keys():
        twinDict['quality'] = qualSwitchDict_webdl[qual]
    
    diff = set(originalDict.iteritems())-set(twinDict.iteritems())
    
    if len(diff):
        return twinDict
    else:
        return None  
    

def ReconstructRelease(version_info, HD, downloadUrl, hearingImpaired):
    # This method reconstructs the original releasename    
    # First split up all components
    parametersList = _ParseVersionInfo(version_info, HD)
    
        
    #First check for unresolvable versions (eg 3 sources combined with multiple qualities)
    problem = _checkIfParseable(parametersList)
    if problem:
        return False
    
    
    releasegroups = parametersList.pop()
    codecs = parametersList.pop()
    qualities = parametersList.pop()
    sources = parametersList.pop()
    
    for x in [sources, qualities, codecs, releasegroups]:
        if not x: x.append(None)
    
    
    
    downloadUrl = [downloadUrl]
    hearingImpaired = [hearingImpaired]
    version_info = [version_info]
    
    # Make version dictionaries
    # Do a cartessian product    
    versionDicts = [
    {'source': sour, 'quality': qual, 'codec': cod, 'releasegrp': rls, 'a7': vers, 'url': url, 'HI': hi}
    for sour, qual, cod, rls, vers, url, hi  in product(sources, qualities, codecs, releasegroups, version_info, downloadUrl, hearingImpaired)
    ]
    
    
    # Check for conflicting entries 
    versionDicts = _checkConflicts(versionDicts)
    if not versionDicts:
        return False

    # Fill in the gaps
    versionDicts = _addInfo(versionDicts)

    twinDicts = []
    for originalDict in versionDicts:
        twinDict = _MakeTwinRelease(originalDict)
        if twinDict:
            twinDicts.append(twinDict)
    
    versionDicts.extend(twinDicts)
    
    return versionDicts


def makeReleaseName(versionInfo, title, season, episode, HI=False):
    version = versionInfo.replace(' ','.')
    se = 'S' + season + 'E' + episode
    release = '.'.join([title,se,version])
    if HI:
        release = release + '.HI'
    return release


def geta7ID(showTitle):
    log.debug('geta7ID: trying to get Addic7ed ID for %s' % showTitle)
    
    imdbID = autosub.Helpers.getShowid(showTitle)
    imdbID = str(imdbID)
    
    # Try the lookup dict first
    if imdbID in a7IdDict.keys():
        show_id = a7IdDict[imdbID]
        log.debug('geta7ID: showid from lookup table %s' % show_id)
        return show_id 
    
    # Do it the old way: lookup official name and try to match with a7 show list
    #TODO: If found, cache it in DB 
    
    # Get the official show name
    if autosub.Helpers.checkAPICallsTvdb(use=False): 
        offShowName = autosub.Tvdb.getShowName(imdbID)
    else:
        log.warning("getShowid: Out of API calls")
        return None
    
    show_ids={}
    try:
        addic7edapi = autosub.Helpers.API('http://www.addic7ed.com/shows.php')
        soup = BeautifulSoup(addic7edapi.resp.read())
        for html_show in soup.select('td.version > h3 > a[href^="/show/"]'):
            show_ids[html_show.string.lower()] = int(html_show['href'][6:])
    except:
        log.error('geta7ID: failed to retrieve a7 show list')
        return None
    
    offShowName = re.compile('%s.*' % offShowName, re.IGNORECASE)
    
    for show in show_ids:
        m = re.match(offShowName, show)
        if m:
            show_id = show_ids[show]
            log.debug('geta7ID: showid for %s from Addic7ed.com search %s' % (showTitle, show_id))
            return show_id
    log.error("geta7ID: Addic7ed ID for %s wasn't found" % showTitle)
    return None

    
class Addic7edAPI():
    def __init__(self):
        self.session = requests.Session()
        self.server = 'http://www.addic7ed.com'
        self.session.headers = {'User-Agent': autosub.USERAGENT}        
        addic7eduser = None
        addic7edpasswd = None
        self.logged_in = False
                
    def login(self, addic7eduser=None, addic7edpasswd=None):        
        log.debug('Addic7edAPI: Logging in')
        
        # Expose to test login
        # When fields are empty it will check the config file
        if not addic7eduser:
            addic7eduser = autosub.ADDIC7EDUSER
        
        if not addic7edpasswd:
            addic7edpasswd = autosub.ADDIC7EDPASSWD
        
        if addic7eduser == u"" or addic7edpasswd == u"":
            log.error('Addic7edAPI: Username and password must be specified')
            return False

        data = {'username': addic7eduser, 'password': addic7edpasswd, 'Submit': 'Log in'}
        try:
            r = self.session.post(self.server + '/dologin.php', data, timeout=10, allow_redirects=False)
        except requests.Timeout:
            log.debug('Addic7edAPI: Timeout after 10 seconds')
        if r.status_code == 302:
            log.info('Addic7edAPI: Logged in')
            self.logged_in = True
            return True
        else:
            log.error('Addic7edAPI: Failed to login')
            return False

    def logout(self):
        if self.logged_in:
            try:
                r = self.session.get(self.server + '/logout.php', timeout=10)
                log.info('Addic7edAPI: Logged out')
            except requests.Timeout:
                log.debug('Addic7edAPI: Timeout after 10 seconds')
            if r.status_code != 200:
                log.error('Addic7edAPI: Request failed with status code %d' % r.status_code)
        self.session.close()

    def get(self, url):
        """
        Make a GET request on `url`
        :param string url: part of the URL to reach with the leading slash
        :rtype: :class:`bs4.BeautifulSoup`
        """
        
        if not self.logged_in:
            log.error("Addic7edAPI: You are not properly logged in. Check your credentials!")
            return None
        try:
            r = self.session.get(self.server + url, timeout=10)
        except requests.Timeout:
            log.debug('Addic7edAPI: Timeout after 10 seconds')
        if r.status_code != 200:
            log.error('Addic7edAPI: Request failed with status code %d' % r.status_code)

        log.debug("Addic7edAPI: Resting for 6 seconds to prevent errors")
        time.sleep(6) #Max 0.5 connections each second
        return BeautifulSoup(r.content) # , 'html5lib')

    def download(self, downloadlink):
        if not self.logged_in:
            log.error("Addic7edAPI: You are not properly logged in. Check your credentials!")
            return None
        
        try:
            r = self.session.get(self.server + downloadlink, timeout=10, headers={'Referer': autosub.USERAGENT})
        except requests.Timeout:
            log.error('Addic7edAPI: Timeout after 10 seconds')
        if r.status_code != 200:
            log.error('Addic7edAPI: Request failed with status code %d' % r.status_code)
        else:
            log.debug('Addic7edAPI: Request succesful with status code %d' % r.status_code)
        
        if r.headers['Content-Type'] == 'text/html':
            log.error('Addic7edAPI: Expected srt file but got HTML; report this!')
            log.debug("Addic7edAPI: Response content: %s" % r.content)
            return None
        log.debug("Addic7edAPI: Resting for 6 seconds to prevent errors")
        time.sleep(6) #Max 0.5 connections each second
        return r.content
    
    def checkCurrentDownloads(self, logout=True):      
        self.login()
            
        try:
            soup = self.get('/panel.php')
            countTag = soup.select('a[href^="mydownloads.php"]')
            pattern = re.compile('(\d*).*of.*\d*', re.IGNORECASE)
            myDownloads = countTag[0].text if countTag else False
            count = re.search(pattern, myDownloads).group(1)
            autosub.DOWNLOADS_A7 = int(count)
        except:
            log.error("Addic7edAPI: Couldn't retrieve current download count")
            return False
        
        if logout:
            self.logout()
        
        return True
            
    def determineAccountType(self):
        self.login()        

        soup = self.get('/panel.php')        
        classTag = soup.select("tr")[20]
        account = classTag.select("td")[1].string
                
        self.logout()
        return account

'''Lookup table for a7 IDs (23/12/'12)
   Key = IMDB ID
   Value = a7 ID
'''
a7IdDict = {
          '0472027' : '328',
          '0437005' : '909',
          '2222135' : '3023',
          '0074028' : '1564',
          '0081856' : '2063',
          '1845887' : '2378',
          '1344204' : '734',
          '1068899' : '3225',
          '2217759' : '3337',
          '0441718' : '1278',
          '2340720' : '3017',
          '2654580' : '4100',
          '0118401' : '807',
          '0058855' : '1900',
          '1181716' : '715',
          '2294227' : '3106',
          '1001558' : '427',
          '1179817' : '359',
          '1322780' : '1828',
          '1059475' : '358',
          '0229898' : '1484',
          '0337792' : '314',
          '0052504' : '1575',
          '1650862' : '1273',
          '1321805' : '526',
          '1713938' : '1521',
          '1651063' : '934',
          '1103973' : '374',
          '0453422' : '1528',
          '2103538' : '3947',
          '1936532' : '2766',
          '0354262' : '2214',
          '0238793' : '2607',
          '0437741' : '1930',
          '2396953' : '3791',
          '1998816' : '1849',
          '2197797' : '2935',
          '2303367' : '2294',
          '1663666' : '915',
          '0085079' : '2079',
          '0361256' : '309',
          '2950766' : '3973',
          '1103968' : '356',
          '2211457' : '3241',
          '0275137' : '2351',
          '1551632' : '984',
          '0966151' : '381',
          '1636691' : '853',
          '1839497' : '1804',
          '0783328' : '265',
          '2274800' : '3089',
          '0083470' : '1565',
          '2193053' : '3362',
          '0112067' : '3815',
          '1305826' : '3067',
          '1474684' : '875',
          '0088512' : '4086',
          '0343230' : '1555',
          '1381020' : '3779',
          '1561756' : '956',
          '0783335' : '2921',
          '1893438' : '1620',
          '3059532' : '3922',
          '0160904' : '218',
          '1349938' : '311',
          '1495708' : '986',
          '2188249' : '2207',
          '2559390' : '4049',
          '1736341' : '1908',
          '2188671' : '3496',
          '1760165' : '1230',
          '1101009' : '1523',
          '0823333' : '191',
          '1285482' : '345',
          '2390791' : '3387',
          '1691602' : '1289',
          '0086822' : '685',
          '0175058' : '3364',
          '0328733' : '3510',
          '1349600' : '3663',
          '0908454' : '420',
          '0397306' : '186',
          '2259665' : '3963',
          '1822469' : '1698',
          '2787218' : '3535',
          '2094262' : '3572',
          '1516278' : '641',
          '2069311' : '1887',
          '2584174' : '3604',
          '0472984' : '1636',
          '0107058' : '3970',
          '0056777' : '461',
          '1728860' : '1346',
          '1397248' : '846',
          '1131746' : '1003',
          '0076996' : '2020',
          '2393813' : '3634',
          '0805661' : '38',
          '0947799' : '270',
          '0115163' : '589',
          '2340036' : '3676',
          '2193041' : '3014',
          '1874066' : '2790',
          '1800493' : '1539',
          '1553620' : '1272',
          '0078570' : '1088',
          '0112230' : '478',
          '1690621' : '994',
          '0118266' : '1030',
          '0207885' : '3059',
          '0274988' : '18',
          '1830332' : '1758',
          '2193185' : '3955',
          '0118276' : '334',
          '0810722' : '741',
          '0058791' : '2069',
          '2582590' : '3635',
          '2226342' : '3759',
          '0374455' : '33',
          '1564623' : '2394',
          '1336582' : '1181',
          '1605467' : '1165',
          '0238784' : '29',
          '0123816' : '1169',
          '0086815' : '1563',
          '1466797' : '867',
          '0285333' : '209',
          '1823011' : '1861',
          '1528509' : '1437',
          '1618371' : '1302',
          '0204993' : '214',
          '1676462' : '3531',
          '1002892' : '1381',
          '1636406' : '762',
          '1587678' : '1511',
          '0938567' : '219',
          '1544603' : '921',
          '0212671' : '122',
          '0395404' : '2434',
          '1929678' : '1585',
          '0072572' : '653',
          '0297494' : '1567',
          '0070996' : '3533',
          '0486657' : '11',
          '0105950' : '1933',
          '1604099' : '787',
          '1967685' : '1853',
          '1798695' : '2803',
          '1279972' : '783',
          '1671577' : '2028',
          '0073990' : '4164',
          '0320038' : '1040',
          '0403795' : '429',
          '2842730' : '3588',
          '0406404' : '2777',
          '1830888' : '2032',
          '0101120' : '1295',
          '0386907' : '263',
          '1958961' : '2234',
          '1055238' : '3715',
          '0934814' : '125',
          '1044196' : '495',
          '1996607' : '3071',
          '0928414' : '279',
          '1321865' : '1996',
          '1578887' : '2051',
          '1536735' : '2896',
          '1268797' : '1087',
          '1556078' : '1312',
          '0840196' : '157',
          '1319735' : '479',
          '0348913' : '188',
          '1910674' : '2004',
          '0058812' : '1242',
          '2433570' : '4141',
          '0757127' : '2277',
          '0321018' : '724',
          '0056757' : '686',
          '0138959' : '726',
          '0115270' : '524',
          '0386950' : '3430',
          '1217208' : '513',
          '2087571' : '2835',
          '0111999' : '1617',
          '1714204' : '2655',
          '1280629' : '445',
          '0429318' : '1243',
          '1267170' : '743',
          '1837642' : '1780',
          '2431738' : '3408',
          '0309125' : '1436',
          '1509004' : '1865',
          '0213523' : '1477',
          '0076987' : '2048',
          '1446633' : '1208',
          '2074248' : '2073',
          '0799862' : '452',
          '1117552' : '351',
          '1494829' : '943',
          '0402711' : '72',
          '0106079' : '1220',
          '0770652' : '610',
          '2441214' : '3002',
          '1531804' : '662',
          '0465315' : '2819',
          '0112123' : '194',
          '0098904' : '54',
          '1870479' : '2590',
          '0417373' : '1183',
          '2006005' : '1936',
          '2098220' : '3801',
          '0370139' : '3024',
          '1826805' : '1807',
          '1723816' : '2402',
          '1196946' : '376',
          '2056366' : '3246',
          '0078622' : '1552',
          '2022713' : '2919',
          '0758745' : '22',
          '2771780' : '3625',
          '2245386' : '3278',
          '2223794' : '3006',
          '1666217' : '1193',
          '2521668' : '3138',
          '0426688' : '652',
          '1661326' : '1202',
          '0200276' : '200',
          '1974934' : '2095',
          '1442435' : '623',
          '1252374' : '437',
          '3173854' : '4122',
          '1657260' : '1228',
          '0103359' : '1602',
          '1592226' : '1066',
          '0367274' : '564',
          '0485301' : '63',
          '2342652' : '4121',
          '0165581' : '945',
          '0179552' : '1231',
          '0395843' : '136',
          '2429840' : '3335',
          '0773262' : '672',
          '1453159' : '985',
          '0101169' : '592',
          '1564698' : '4087',
          '0283775' : '339',
          '0075592' : '3152',
          '2401129' : '3279',
          '1392247' : '845',
          '1720619' : '2038',
          '2616280' : '2397',
          '1441939' : '1109',
          '0424600' : '330',
          '0041037' : '1306',
          '2137109' : '3994',
          '1563069' : '1294',
          '2303123' : '2488',
          '1596259' : '926',
          '0112194' : '585',
          '0173587' : '1687',
          '2252938' : '4149',
          '1385167' : '421',
          '0496356' : '1008',
          '1340758' : '3304',
          '2708560' : '3852',
          '0129711' : '3215',
          '0283203' : '664',
          '0108949' : '3342',
          '2298477' : '4026',
          '0965394' : '379',
          '0874608' : '887',
          '1094229' : '1154',
          '1612578' : '1073',
          '2091127' : '2043',
          '1742965' : '1959',
          '0086770' : '1157',
          '1551948' : '2172',
          '0168326' : '442',
          '1772157' : '2785',
          '0165564' : '1840',
          '0475047' : '528',
          '2294189' : '3677',
          '0094540' : '2904',
          '2065460' : '2571',
          '1830622' : '1666',
          '2883562' : '3949',
          '1777715' : '1223',
          '0778908' : '2606',
          '0460690' : '40',
          '1219836' : '516',
          '0105943' : '521',
          '1435958' : '636',
          '0423731' : '1083',
          '2799012' : '4064',
          '1186356' : '386',
          '0054572' : '1214',
          '1220111' : '2410',
          '0450897' : '2697',
          '0103520' : '4012',
          '0108756' : '678',
          '1816993' : '1651',
          '0058824' : '2112',
          '1010360' : '2703',
          '0103442' : '1089',
          '0187636' : '502',
          '2368645' : '3871',
          '2487090' : '3754',
          '0279600' : '10',
          '1188927' : '562',
          '1247637' : '729',
          '1531273' : '767',
          '0361217' : '77',
          '0450898' : '951',
          '1411254' : '849',
          '1960029' : '3090',
          '0159090' : '987',
          '0073961' : '772',
          '1609540' : '941',
          '1422234' : '1813',
          '0862614' : '1293',
          '0413573' : '30',
          '2010086' : '2213',
          '2189221' : '3537',
          '1327801' : '466',
          '1759761' : '2420',
          '1276321' : '393',
          '0364828' : '104',
          '0136684' : '931',
          '0865546' : '1363',
          '2400736' : '3979',
          '0058796' : '3022',
          '1497609' : '1029',
          '0069602' : '1638',
          '1484577' : '964',
          '0259786' : '2231',
          '0760437' : '942',
          '0115369' : '1212',
          '0144069' : '1414',
          '1704292' : '3096',
          '2223236' : '2652',
          '0220915' : '3819',
          '0874936' : '140',
          '1458830' : '4125',
          '2226397' : '3549',
          '0094982' : '1084',
          '0384013' : '1499',
          '1738180' : '3172',
          '2261103' : '2262',
          '1449940' : '1320',
          '0108771' : '638',
          '2402807' : '2842',
          '2372220' : '3777',
          '1129398' : '3712',
          '3012184' : '3608',
          '1618457' : '3231',
          '0118475' : '1135',
          '1958752' : '1669',
          '0955250' : '167',
          '0364829' : '970',
          '2886812' : '4033',
          '1031283' : '1368',
          '2281583' : '2877',
          '0434672' : '1124',
          '0115167' : '499',
          '3239918' : '4055',
          '0481449' : '1397',
          '1685471' : '1119',
          '0880557' : '127',
          '2089467' : '1905',
          '0460631' : '647',
          '2861424' : '4166',
          '2491332' : '3064',
          '0945090' : '3806',
          '0936458' : '369',
          '0914387' : '111',
          '1458796' : '4075',
          '0058811' : '625',
          '2240991' : '2813',
          '0423642' : '1981',
          '1297754' : '736',
          '2294225' : '2314',
          '0348914' : '69',
          '1844624' : '1799',
          '2329077' : '3864',
          '0387779' : '1372',
          '0485842' : '75',
          '0088478' : '3134',
          '0384766' : '73',
          '2254256' : '2591',
          '2480514' : '3490',
          '1086191' : '1776',
          '1710308' : '2867',
          '1086788' : '451',
          '1240976' : '444',
          '0472023' : '605',
          '0491738' : '47',
          '2367061' : '2013',
          '1305562' : '506',
          '0115285' : '1033',
          '1330768' : '1796',
          '0094466' : '1909',
          '0844653' : '364',
          '0497298' : '99',
          '0267201' : '2971',
          '0106080' : '630',
          '1213404' : '329',
          '0362357' : '303',
          '1640175' : '1078',
          '2017109' : '3239',
          '1451387' : '922',
          '1229413' : '519',
          '1112285' : '377',
          '0184157' : '3805',
          '2699288' : '3766',
          '1809362' : '1459',
          '1442550' : '2391',
          '1400580' : '607',
          '1909015' : '3211',
          '1820166' : '3372',
          '1707807' : '1751',
          '1659175' : '1546',
          '1332030' : '518',
          '1409008' : '958',
          '1055335' : '1979',
          '0907831' : '1912',
          '0898266' : '126',
          '0197182' : '1412',
          '1610527' : '1488',
          '0220189' : '1892',
          '2303687' : '2594',
          '0248654' : '407',
          '1307824' : '660',
          '1807165' : '2300',
          '1827070' : '2923',
          '1001482' : '371',
          '1697033' : '2372',
          '2355844' : '3506',
          '0318224' : '855',
          '1826951' : '2136',
          '0867015' : '666',
          '1229401' : '353',
          '0101049' : '248',
          '0809497' : '142',
          '1954804' : '2546',
          '1483024' : '663',
          '2751228' : '4070',
          '2216156' : '3111',
          '2311643' : '2828',
          '0310455' : '790',
          '0775558' : '411',
          '1085251' : '759',
          '0206501' : '3013',
          '0364817' : '431',
          '1991897' : '2163',
          '3084090' : '3896',
          '0108961' : '1356',
          '0412175' : '220',
          '2407574' : '3245',
          '0118254' : '257',
          '1204507' : '317',
          '0115378' : '553',
          '1611787' : '776',
          '0108758' : '258',
          '2748608' : '3567',
          '0386180' : '2443',
          '0848539' : '129',
          '0096531' : '1143',
          '1794147' : '2166',
          '0057798' : '1949',
          '0770521' : '59',
          '1217239' : '365',
          '1713938' : '352',
          '1430509' : '1158',
          '0276736' : '385',
          '2290339' : '3012',
          '0185906' : '559',
          '0256566' : '2662',
          '2155025' : '3446',
          '2245283' : '3649',
          '0499591' : '408',
          '1758772' : '1623',
          '2296682' : '4069',
          '2660734' : '4040',
          '0129695' : '1190',
          '0073972' : '1801',
          '1934818' : '1624',
          '0398599' : '1558',
          '1379722' : '864',
          '1842127' : '1507',
          '0098798' : '545',
          '0063950' : '1568',
          '1512807' : '1112',
          '2239949' : '2263',
          '0129692' : '3130',
          '0090481' : '581',
          '1590961' : '1416',
          '1521186' : '2902',
          '1353056' : '3739',
          '0096560' : '1407',
          '2372182' : '3995',
          '0081912' : '262',
          '0187664' : '210',
          '0458259' : '2880',
          '0448190' : '114',
          '1854226' : '1422',
          '0428174' : '470',
          '0499400' : '1649',
          '0294023' : '2399',
          '1558128' : '1288',
          '0068112' : '2942',
          '0975412' : '3900',
          '1389371' : '937',
          '1834598' : '1343',
          '1197632' : '354',
          '2584174' : '3615',
          '1877712' : '2169',
          '0433309' : '74',
          '1780441' : '1303',
          '0372053' : '4152',
          '2443980' : '3255',
          '2262383' : '2913',
          '0088631' : '1693',
          '0885761' : '531',
          '2712740' : '3967',
          '0804503' : '108',
          '1183569' : '475',
          '1655078' : '896',
          '0134246' : '3150',
          '1533395' : '831',
          '0830900' : '141',
          '1783495' : '1708',
          '2288064' : '4036',
          '1672189' : '1406',
          '0799893' : '3651',
          '1674553' : '4129',
          '1427816' : '1501',
          '0083500' : '1010',
          '2262308' : '2966',
          '2442560' : '3990',
          '0043208' : '2786',
          '1599374' : '1515',
          '0227912' : '3159',
          '1874838' : '1470',
          '0835434' : '249',
          '2391224' : '2914',
          '0959601' : '2266',
          '1068912' : '760',
          '0397138' : '2407',
          '0115320' : '477',
          '1853789' : '1716',
          '0077016' : '3322',
          '2215842' : '3244',
          '0493229' : '3817',
          '0101226' : '3703',
          '1755893' : '1318',
          '1703925' : '1670',
          '0118364' : '599',
          '0214362' : '1017',
          '0106145' : '692',
          '1812523' : '2489',
          '0495055' : '2718',
          '2222352' : '2912',
          '0416394' : '1222',
          '1743904' : '2130',
          '1582453' : '1283',
          '1819509' : '2349',
          '0805666' : '42',
          '0458290' : '362',
          '2341339' : '2760',
          '1692202' : '1399',
          '0979432' : '1075',
          '1926955' : '2071',
          '1679482' : '1509',
          '1830491' : '2036',
          '2176609' : '4143',
          '0477217' : '3950',
          '0460091' : '31',
          '2321708' : '3170',
          '1981558' : '2264',
          '1641349' : '1786',
          '2497834' : '3885',
          '3292510' : '4104',
          '2677314' : '3412',
          '1706532' : '2414',
          '1875471' : '1513',
          '2183641' : '3205',
          '1480669' : '1189',
          '0163953' : '574',
          '0103405' : '1593',
          '1343865' : '1703',
          '1864750' : '4106',
          '0866432' : '58',
          '1854004' : '3671',
          '2144753' : '2070',
          '2535732' : '3912',
          '1713288' : '1592',
          '1888795' : '1697',
          '2480498' : '3670',
          '1885102' : '3157',
          '1583607' : '944',
          '0435937' : '491',
          '1530541' : '2432',
          '0092357' : '537',
          '1127876' : '2195',
          '0368530' : '64',
          '1169424' : '469',
          '3012160' : '4111',
          '0955353' : '162',
          '1984988' : '1817',
          '0936451' : '3414',
          '2455546' : '3705',
          '1826989' : '2153',
          '1718438' : '1101',
          '0084967' : '1048',
          '1797629' : '1433',
          '1600199' : '1598',
          '1701920' : '1550',
          '0092319' : '4123',
          '1595860' : '955',
          '0445912' : '1007',
          '0197154' : '1434',
          '0307427' : '2898',
          '0086249' : '824',
          '0955322' : '117',
          '2477858' : '3386',
          '2141869' : '3770',
          '0460649' : '51',
          '0108894' : '2114',
          '1811399' : '2261',
          '1698158' : '1309',
          '1866570' : '3179',
          '0114327' : '4150',
          '1582350' : '1279',
          '0476918' : '900',
          '2334302' : '2830',
          '0403783' : '586',
          '0074074' : '546',
          '0112175' : '3074',
          '1688779' : '989',
          '0098878' : '471',
          '0284718' : '484',
          '0843548' : '4158',
          '0373732' : '871',
          '0096697' : '120',
          '0247827' : '1170',
          '2700678' : '3547',
          '2319283' : '2889',
          '1524993' : '3415',
          '0318252' : '1134',
          '1596589' : '1571',
          '0105929' : '1227',
          '2711738' : '4051',
          '1678053' : '995',
          '2215291' : '3072',
          '1650552' : '1639',
          '0205700' : '1706',
          '1591620' : '1590',
          '2106857' : '2160',
          '1666667' : '1297',
          '0805669' : '66',
          '1231460' : '1250',
          '1843323' : '1795',
          '1621748' : '748',
          '1192169' : '771',
          '1586680' : '1277',
          '0461622' : '1323',
          '0380136' : '1153',
          '1971245' : '2347',
          '0799922' : '661',
          '0821375' : '313',
          '1445201' : '624',
          '1365539' : '2660',
          '2406376' : '3850',
          '2871832' : '3883',
          '2615506' : '4028',
          '0264235' : '96',
          '2245029' : '3185',
          '1582461' : '1836',
          '0147788' : '2780',
          '1183865' : '1648',
          '0050079' : '1145',
          '1405466' : '2900',
          '0903747' : '240',
          '1280822' : '536',
          '0344994' : '1393',
          '2012511' : '2584',
          '0201391' : '554',
          '0315081' : '1361',
          '0157239' : '1171',
          '0460651' : '779',
          '2191613' : '2925',
          '1684734' : '1229',
          '2076610' : '2206',
          '1570987' : '1319',
          '0306414' : '71',
          '2935974' : '3812',
          '0202198' : '542',
          '0106004' : '316',
          '0290988' : '1408',
          '0410975' : '16',
          '1751105' : '2193',
          '0163438' : '1100',
          '0118375' : '775',
          '1001484' : '3884',
          '1641384' : '1234',
          '1333050' : '923',
          '2215052' : '3332',
          '0928173' : '373',
          '0364774' : '925',
          '0086687' : '2030',
          '0805664' : '158',
          '0111880' : '2258',
          '0106179' : '85',
          '2208885' : '2287',
          '0096579' : '1108',
          '0085101' : '2125',
          '0947080' : '341',
          '0101076' : '1240',
          '1444382' : '836',
          '0802148' : '960',
          '0162065' : '558',
          '1552112' : '982',
          '0103484' : '978',
          '2220083' : '2201',
          '1442464' : '628',
          '0111958' : '193',
          '0981216' : '170',
          '0976014' : '164',
          '1723760' : '2559',
          '0061265' : '1891',
          '1024701' : '272',
          '0348983' : '511',
          '0105958' : '1252',
          '1196953' : '841',
          '0397150' : '2888',
          '0876219' : '3382',
          '2166772' : '3258',
          '2318795' : '2285',
          '2427220' : '3803',
          '1935298' : '3033',
          '1641247' : '1980',
          '0826760' : '1380',
          '0948539' : '395',
          '2467372' : '3999',
          '0381798' : '242',
          '2262532' : '3736',
          '0969007' : '236',
          '0103466' : '1275',
          '0098749' : '1042',
          '1625330' : '1298',
          '1232266' : '456',
          '2163315' : '3334',
          '1286039' : '627',
          '0330251' : '20',
          '1663654' : '1522',
          '1868102' : '1663',
          '0801425' : '84',
          '0074048' : '591',
          '1199099' : '375',
          '1518917' : '1938',
          '2647548' : '3998',
          '1148181' : '560',
          '0478079' : '3811',
          '0313043' : '156',
          '1592240' : '1155',
          '0866442' : '474',
          '1986770' : '2605',
          '2008890' : '1779',
          '0158552' : '597',
          '1623136' : '889',
          '0088559' : '520',
          '0363307' : '770',
          '1429449' : '1113',
          '2229907' : '3958',
          '0210413' : '496',
          '0972534' : '708',
          '1289217' : '1731',
          '2632424' : '3898',
          '0460654' : '97',
          '1533010' : '1166',
          '0112095' : '1194',
          '0086661' : '590',
          '1719950' : '1267',
          '0417299' : '175',
          '1840429' : '2156',
          '0088547' : '1347',
          '1135300' : '390',
          '2660806' : '4009',
          '0068128' : '709',
          '0078588' : '1951',
          '0773262' : '6',
          '0220261' : '1478',
          '2215717' : '2891',
          '1480072' : '4061',
          '1489428' : '751',
          '0057751' : '2077',
          '0297494' : '1556',
          '2731624' : '3526',
          '0086779' : '414',
          '0923293' : '416',
          '2795962' : '3643',
          '1657081' : '1079',
          '0285370' : '1719',
          '0060028' : '1537',
          '2964118' : '3763',
          '0092353' : '4039',
          '0118298' : '70',
          '0976192' : '2398',
          '0059977' : '3354',
          '1630574' : '1489',
          '0401995' : '1132',
          '1513168' : '936',
          '0463398' : '1182',
          '2148433' : '2133',
          '0061287' : '579',
          '1853840' : '1512',
          '0362153' : '1206',
          '1797404' : '2147',
          '0276650' : '455',
          '2124494' : '2742',
          '1129029' : '810',
          '1008108' : '261',
          '2209714' : '3080',
          '2086606' : '1922',
          '0383126' : '757',
          '1798701' : '3115',
          '1837654' : '1800',
          '1887517' : '1975',
          '0085037' : '691',
          '1208358' : '839',
          '1332071' : '397',
          '1329291' : '703',
          '2295809' : '3734',
          '0879688' : '543',
          '0098803' : '1535',
          '0380136' : '1226',
          '0160277' : '613',
          '2183404' : '3613',
          '1568769' : '1064',
          '1724587' : '1987',
          '1515193' : '1022',
          '2309295' : '3603',
          '0115322' : '1373',
          '0096657' : '1014',
          '0600527' : '3749',
          '0493197' : '1895',
          '1684910' : '1378',
          '1118697' : '357',
          '0072500' : '285',
          '0852863' : '3626',
          '0312172' : '82',
          '0115157' : '1767',
          '0790820' : '80',
          '1178522' : '396',
          '1595856' : '1259',
          '0482439' : '4154',
          '0387764' : '668',
          '0083399' : '196',
          '0085011' : '2000',
          '2394340' : '3544',
          '0066722' : '1140',
          '0065327' : '2078',
          '1674023' : '1015',
          '1415889' : '764',
          '1366312' : '635',
          '0796264' : '94',
          '0408378' : '3577',
          '1610515' : '1071',
          '2603596' : '4011',
          '0398427' : '3941',
          '1409646' : '472',
          '2200255' : '2769',
          '2634230' : '3680',
          '0788121' : '3938',
          '0397442' : '121',
          '0098898' : '1803',
          '1358522' : '659',
          '0072567' : '2092',
          '0115341' : '1006',
          '1077744' : '567',
          '1734537' : '1097',
          '3098828' : '4058',
          '2156187' : '2468',
          '2446726' : '3923',
          '0813808' : '3786',
          '0069637' : '1531',
          '1820950' : '1428',
          '1568202' : '992',
          '2224119' : '3389',
          '0490035' : '1336',
          '1949012' : '2150',
          '0215693' : '910',
          '1600194' : '1060',
          '0376390' : '4014',
          '1441096' : '614',
          '2129898' : '2820',
          '0481452' : '643',
          '1708523' : '3589',
          '2249364' : '3438',
          '0487189' : '1162',
          '0118984' : '343',
          '0808096' : '60',
          '2070791' : '2856',
          '2136967' : '2121',
          '0409608' : '1324',
          '2375720' : '3319',
          '0108723' : '706',
          '2802008' : '4044',
          '1346018' : '572',
          '1739276' : '1672',
          '1615926' : '1062',
          '0457146' : '1953',
          '0379632' : '138',
          '1511543' : '996',
          '0086817' : '1881',
          '0756509' : '41',
          '1145872' : '769',
          '1832668' : '873',
          '0075527' : '2091',
          '0948538' : '134',
          '0862593' : '105',
          '0175058' : '3934',
          '0936453' : '363',
          '1657505' : '1677',
          '3061046' : '4077',
          '1119644' : '350',
          '2210264' : '2733',
          '2071322' : '3166',
          '1667715' : '1486',
          '2358629' : '3086',
          '1591105' : '1360',
          '1643266' : '859',
          '1587669' : '1068',
          '0367344' : '501',
          '0243069' : '718',
          '0362192' : '462',
          '1726576' : '1168',
          '1591493' : '1038',
          '1666278' : '1725',
          '2191671' : '2864',
          '1504261' : '1311',
          '0439879' : '1239',
          '0423668' : '252',
          '0460644' : '143',
          '1652218' : '1369',
          '1117666' : '508',
          '1440346' : '634',
          '0092379' : '1200',
          '0455253' : '594',
          '0318883' : '485',
          '2130271' : '3057',
          '1498094' : '865',
          '2647544' : '3997',
          '0429378' : '1241',
          '0428134' : '872',
          '1258216' : '1911',
          '1480684' : '1118',
          '1628033' : '197',
          '0386676' : '65',
          '0075472' : '2688',
          '2649480' : '3616',
          '2243973' : '3550',
          '0193676' : '172',
          '0460619' : '509',
          '1930076' : '4071',
          '2710104' : '4019',
          '0096555' : '1738',
          '0310443' : '1021',
          '1888075' : '1927',
          '0286486' : '17',
          '1945796' : '1679',
          '1438437' : '949',
          '0280257' : '1046',
          '2560206' : '3191',
          '1402376' : '618',
          '0262985' : '541',
          '0053502' : '1526',
          '0235137' : '2062',
          '0057773' : '284',
          '1477819' : '658',
          '1442449' : '720',
          '0098830' : '719',
          '0369179' : '86',
          '1790914' : '1809',
          '0457229' : '183',
          '0221751' : '2454',
          '2533174' : '3108',
          '1955324' : '1815',
          '2923816' : '3940',
          '0068098' : '568',
          '1831575' : '1774',
          '0096708' : '544',
          '0052520' : '1086',
          '2234222' : '3539',
          '0090390' : '280',
          '1299368' : '449',
          '1592154' : '1057',
          '0319931' : '400',
          '0367279' : '267',
          '1830379' : '1948',
          '1728102' : '2149',
          '1327810' : '1102',
          '2306299' : '2964',
          '1983079' : '2176',
          '1695583' : '1367',
          '0944947' : '1245',
          '2069270' : '2376',
          '1625724' : '3121',
          '1124373' : '582',
          '2295953' : '3068',
          '1553644' : '754',
          '1332150' : '517',
          '0219446' : '1126',
          '2263720' : '3036',
          '0278238' : '1121',
          '2337840' : '2768',
          '1275286' : '1682',
          '1571437' : '1762',
          '1693592' : '1543',
          '2397255' : '3552',
          '0169501' : '882',
          '1842530' : '1792',
          '0108968' : '2173',
          '1786211' : '1388',
          '1441135' : '609',
          '0174378' : '1144',
          '1825122' : '2403',
          '0880605' : '2615',
          '0387199' : '52',
          '0076984' : '87',
          '1595859' : '1067',
          '2232345' : '2496',
          '1835129' : '1765',
          '2555256' : '3443',
          '0368479' : '155',
          '0088628' : '1105',
          '2501212' : '3114',
          '1218572' : '800',
          '0214382' : '2744',
          '1140939' : '493',
          '0851851' : '98',
          '1434482' : '3124',
          '2410882' : '2852',
          '1493239' : '1074',
          '0096542' : '1823',
          '1836237' : '1727',
          '0204082' : '1732',
          '0178126' : '1541',
          '1044418' : '697',
          '1565059' : '1410',
          '0494186' : '1287',
          '1586676' : '1281',
          '1462059' : '1652',
          '2025899' : '3582',
          '1315058' : '888',
          '0165961' : '185',
          '0313122' : '2907',
          '1081848' : '1896',
          '2708572' : '3445',
          '2325846' : '2791',
          '2222848' : '2798',
          '1874006' : '1700',
          '2220768' : '3920',
          '0098909' : '826',
          '0103417' : '629',
          '0071054' : '1966',
          '1757202' : '3401',
          '0790772' : '169',
          '0137330' : '1542',
          '0088513' : '281',
          '2649588' : '3952',
          '2520512' : '3689',
          '0134257' : '1748',
          '0206512' : '1622',
          '0159206' : '95',
          '1569972' : '998',
          '1305108' : '382',
          '2763286' : '4097',
          '0289830' : '89',
          '0449461' : '3016',
          '2433738' : '3930',
          '1149608' : '394',
          '1492179' : '879',
          '1122770' : '460',
          '1695360' : '2350',
          '2290981' : '2532',
          '0988820' : '667',
          '1044418' : '965',
          '0259733' : '595',
          '1196947' : '348',
          '1976151' : '1420',
          '1353056' : '3740',
          '1484498' : '903',
          '0775374' : '957',
          '0426371' : '894',
          '1203167' : '1377',
          '1159605' : '418',
          '0496343' : '45',
          '0115288' : '535',
          '0787490' : '370',
          '0285351' : '575',
          '2883224' : '4113',
          '2297363' : '2561',
          '0105946' : '205',
          '1786704' : '1676',
          '0051305' : '683',
          '1615925' : '1675',
          '0491603' : '384',
          '1591511' : '966',
          '1663676' : '1704',
          '1094248' : '321',
          '0083402' : '1920',
          '0115082' : '1423',
          '0367345' : '503',
          '0115083' : '1493',
          '0055683' : '2702',
          '0944317' : '967',
          '3259470' : '4065',
          '1779872' : '2775',
          '0207275' : '1492',
          '2741602' : '4008',
          '1492030' : '1463',
          '0262150' : '68',
          '1699748' : '1814',
          '0210418' : '3351',
          '2726918' : '3769',
          '0092345' : '2019',
          '0144727' : '1364',
          '1270367' : '532',
          '2520946' : '4144',
          '1179914' : '439',
          '1122769' : '515',
          '0364845' : '132',
          '1043714' : '684',
          '1219817' : '904',
          '2794380' : '3936',
          '1225790' : '457',
          '0810788' : '107',
          '0285331' : '7',
          '0247082' : '57',
          '0935095' : '372',
          '1695989' : '1172',
          '0086659' : '863',
          '2203421' : '3688',
          '1695366' : '3021',
          '0337791' : '1387',
          '0108717' : '1495',
          '1722512' : '2373',
          '2569488' : '3760',
          '0136643' : '2080',
          '2310212' : '3217',
          '1352077' : '1490',
          '0439100' : '81',
          '1517121' : '1929',
          '2069449' : '2952',
          '1675276' : '3525',
          '1281313' : '850',
          '1752076' : '3127',
          '0112173' : '780',
          '0485617' : '2968',
          '2090440' : '3600',
          '0244365' : '1236',
          '1245695' : '468',
          '1726839' : '1548',
          '0412142' : '15',
          '0108734' : '2430',
          '1949720' : '2097',
          '2402129' : '3762',
          '1166893' : '403',
          '1243719' : '763',
          '1690364' : '1859',
          '0080306' : '264',
          '1847521' : '1502',
          '1442065' : '961',
          '1985443' : '2518',
          '0098936' : '235',
          '1607037' : '2700',
          '0103586' : '3716',
          '0290966' : '655',
          '0496275' : '213',
          '0455275' : '4',
          '1588224' : '821',
          '1822448' : '1376',
          '0287839' : '1204',
          '2372806' : '3597',
          '0078680' : '1560',
          '0423646' : '282',
          '2712966' : '4013',
          '0307716' : '1615',
          '1827733' : '1345',
          '1707394' : '1359',
          '0377248' : '1425',
          '0346314' : '3887',
          '1631891' : '1256',
          '1843678' : '1588',
          '0259141' : '1768',
          '0060010' : '3776',
          '1219024' : '424',
          '0775362' : '1237',
          '0320037' : '959',
          '2699780' : '4006',
          '2006374' : '2792',
          '0088634' : '1718',
          '1826940' : '1784',
          '1866609' : '1764',
          '1748166' : '947',
          '0805668' : '83',
          '1702042' : '1339',
          '1830617' : '1806',
          '1103987' : '360',
          '1319636' : '530',
          '0184135' : '793',
          '0221735' : '3800',
          '1312022' : '814',
          '0090461' : '2082',
          '1697793' : '1362',
          '0101143' : '3590',
          '1558182' : '1159',
          '0481459' : '907',
          '2242025' : '2764',
          '1787217' : '1740',
          '0241383' : '4084',
          '2372162' : '3861',
          '0066626' : '1524',
          '0098837' : '286',
          '1525182' : '1016',
          '0135093' : '4032',
          '0840094' : '777',
          '0103429' : '4138',
          '0462128' : '260',
          '1797475' : '1789',
          '1864016' : '2083',
          '1554369' : '3120',
          '1606375' : '1149',
          '2255085' : '1825',
          '0477507' : '2109',
          '2766052' : '3927',
          '2407838' : '3256',
          '0421033' : '1370',
          '0348894' : '898',
          '0071042' : '1824',
          '1612434' : '827',
          '2199618' : '3623',
          '2551252' : '3975',
          '0294004' : '2272',
          '0068149' : '2103',
          '1421054' : '835',
          '1132290' : '525',
          '1596356' : '1056',
          '2172103' : '2883',
          '0429466' : '747',
          '1220617' : '337',
          '1299365' : '750',
          '2300923' : '2751',
          '0092325' : '2050',
          '0062578' : '1940',
          '0112130' : '527',
          '1819545' : '1787',
          '2584098' : '3605',
          '2006421' : '2956',
          '1919418' : '1721',
          '0203248' : '402',
          '0220906' : '832',
          '1246607' : '446',
          '2122954' : '2157',
          '1468773' : '3032',
          '1839578' : '1802',
          '2338232' : '4018',
          '0285335' : '181',
          '1806234' : '1308',
          '0756582' : '118',
          '0077089' : '1747',
          '1086761' : '1094',
          '1582459' : '1058',
          '1213218' : '791',
          '2404029' : '2851',
          '1943524' : '2152',
          '1227637' : '551',
          '0066701' : '1827',
          '0839188' : '154',
          '1883814' : '646',
          '0210455' : '1570',
          '2510712' : '3088',
          '1844923' : '1413',
          '2022170' : '2390',
          '1743880' : '2154',
          '1727434' : '1657',
          '0115151' : '2270',
          '1307789' : '3517',
          '0446809' : '818',
          '1717455' : '1395',
          '0409570' : '253',
          '1769803' : '1409',
          '1954347' : '2511',
          '2201416' : '2562',
          '0907702' : '398',
          '0482857' : '561',
          '2239947' : '2677',
          '1406662' : '758',
          '0765458' : '1201',
          '2655470' : '3965',
          '0106126' : '266',
          '0094582' : '1167',
          '1159996' : '2182',
          '1830351' : '1286',
          '0494287' : '225',
          '0074006' : '1967',
          '1772379' : '1834',
          '1524415' : '2040',
          '0904208' : '109',
          '1582457' : '1442',
          '0083505' : '1411',
          '1157595' : '346',
          '0765425' : '815',
          '1477131' : '739',
          '1545214' : '1965',
          '1441093' : '899',
          '2249007' : '3783',
          '2281375' : '2976',
          '0203268' : '1264',
          '1329539' : '1394',
          '1250890' : '480',
          '0068135' : '1899',
          '1050057' : '347',
          '2073864' : '3300',
          '2321596' : '3981',
          '0288937' : '322',
          '0302103' : '522',
          '0073995' : '245',
          '0054531' : '1065',
          '0108988' : '1251',
          '0249301' : '1352',
          '0094535' : '166',
          '0352110' : '2363',
          '0088571' : '2074',
          '0805667' : '622',
          '0111873' : '1494',
          '1439629' : '611',
          '0115231' : '1989',
          '1232714' : '908',
          '1220137' : '489',
          '2715776' : '4030',
          '1832045' : '2366',
          '1442437' : '620',
          '1127205' : '2588',
          '0477496' : '1496',
          '1608383' : '2723',
          '1978940' : '3100',
          '1441106' : '860',
          '2286877' : '2344',
          '1698441' : '1195',
          '0757084' : '2212',
          '1839683' : '2246',
          '1850458' : '1811',
          '2453016' : '3229',
          '0078579' : '1880',
          '2078467' : '2041',
          '0928410' : '145',
          '2049576' : '3213',
          '0206476' : '221',
          '1865769' : '1874',
          '0065314' : '1219',
          '0463827' : '3084',
          '0398417' : '1594',
          '2215399' : '3380',
          '0105932' : '1191',
          '0076993' : '1557',
          '2782214' : '3521',
          '0442715' : '4016',
          '1652654' : '1426',
          '0069572' : '1076',
          '0460692' : '184',
          '2712612' : '3831',
          '0324679' : '918',
          '0112167' : '217',
          '0400037' : '278',
          '2336352' : '2763',
          '0147760' : '1514',
          '1771224' : '1668',
          '1259574' : '980',
          '1678749' : '1904',
          '0294097' : '324',
          '1638319' : '1307',
          '0374463' : '753',
          '3130096' : '2464',
          '1620950' : '1357',
          '1232320' : '447',
          '1262403' : '404',
          '0991266' : '1334',
          '1886866' : '1759',
          '2184980' : '3247',
          '0085112' : '578',
          '2378794' : '4024',
          '1470018' : '3935',
          '2039333' : '2126',
          '1380596' : '1427',
          '1492090' : '2843',
          '0068093' : '215',
          '0346369' : '929',
          '0408381' : '1018',
          '0265755' : '1673',
          '0758790' : '46',
          '0092400' : '144',
          '2071236' : '2855',
          '0083480' : '1690',
          '2248977' : '2908',
          '1796960' : '1812',
          '0459159' : '552',
          '0112178' : '415',
          '1520211' : '1175',
          '1995142' : '2215',
          '0321021' : '173',
          '0898332' : '161',
          '0098948' : '1505',
          '1441109' : '619',
          '0081874' : '1580',
          '0808013' : '44',
          '0273366' : '387',
          '0414731' : '497',
          '1629348' : '3135',
          '0202748' : '512',
          '0320969' : '3487',
          '0096684' : '587',
          '1829891' : '1660',
          '1195935' : '523',
          '1119176' : '435',
          '0493100' : '1894',
          '0094521' : '571',
          '0377253' : '2626',
          '3086936' : '4027',
          '1942147' : '1674',
          '1181917' : '976',
          '0837143' : '428',
          '1219818' : '711',
          '0118363' : '806',
          '0429455' : '1508',
          '0071036' : '3321',
          '0057733' : '1274',
          '0063962' : '1551',
          '1233514' : '1631',
          '0327375' : '803',
          '2647258' : '4007',
          '0458253' : '90',
          '1842973' : '1820',
          '0974077' : '422',
          '0086759' : '950',
          '0960136' : '135',
          '0159145' : '3393',
          '2186101' : '2884',
          '0362359' : '37',
          '0293741' : '2474',
          '1865572' : '1886',
          '0103362' : '2632',
          '0429422' : '294',
          '1287231' : '433',
          '2122080' : '3755',
          '2757532' : '3448',
          '1842793' : '1390',
          '2476706' : '3653',
          '2256491' : '2834',
          '0178149' : '602',
          '1749004' : '1265',
          '1108394' : '539',
          '0072564' : '1316',
          '0421030' : '76',
          '0220008' : '440',
          '2705602' : '1553',
          '0454753' : '651',
          '0452046' : '21',
          '0497578' : '713',
          '2350760' : '3475',
          '1688606' : '1391',
          '1703874' : '1382',
          '1647865' : '842',
          '1578258' : '1063',
          '1145500' : '500',
          '2151670' : '2461',
          '0484082' : '583',
          '0047766' : '1561',
          '0397756' : '2580',
          '0098800' : '690',
          '0978537' : '2226',
          '2787278' : '3987',
          '0081919' : '2781',
          '1878805' : '2859',
          '0092351' : '1300',
          '0106084' : '2631',
          '2498086' : '3271',
          '1460746' : '696',
          '0772145' : '834',
          '1873887' : '3775',
          '1464482' : '640',
          '2432604' : '4059',
          '0141842' : '55',
          '0071033' : '419',
          '1366321' : '549',
          '1593756' : '1077',
          '2381048' : '4056',
          '2245117' : '3709',
          '2174367' : '2237',
          '0086661' : '3187',
          '1474316' : '604',
          '2246569' : '2758',
          '0420372' : '207',
          '0343314' : '1969',
          '278271' : '3551',
          '0079902' : '2829',
          '0060036' : '1301',
          '0273399' : '671',
          '1415244' : '548',
          '1832979' : '1790',
          '0074036' : '1742',
          '0389564' : '56',
          '3183264' : '4034',
          '2724068' : '3418',
          '1051155' : '202',
          '0437741' : '816',
          '0787985' : '119',
          '0830361' : '62',
          '1656896' : '1009',
          '0118379' : '216',
          '0485301' : '1692',
          '0319969' : '13',
          '2014554' : '2016',
          '0118300' : '498',
          '1119176' : '2633',
          '0054515' : '3311',
          '1632701' : '1667',
          '1750269' : '1210',
          '1190689' : '476',
          '0337898' : '1019',
          '0058815' : '1125',
          '1955311' : '2137',
          '2584096' : '3607',
          '0134247' : '259',
          '2043143' : '3402',
          '1599357' : '948',
          '2396135' : '3463',
          '0366005' : '1600',
          '1642351' : '862',
          '1721669' : '1686',
          '1745588' : '1578',
          '0375355' : '504',
          '1943276' : '2221',
          '2242910' : '3462',
          '0086765' : '830',
          '0072562' : '368',
          '2649522' : '4074',
          '0056751' : '12',
          '1186331' : '639',
          '2382108' : '3004',
          '2885556' : '3636',
          '0460672' : '1993',
          '2284766' : '3437',
          '0108885' : '946',
          '0941372' : '837',
          '1567215' : '1482',
          '0216894' : '1500',
          '0462139' : '178',
          '1988386' : '2269',
          '0892535' : '244',
          '1127107' : '1142',
          '0092319' : '1133',
          '2177491' : '2885',
          '0910812' : '198',
          '0139776' : '2899',
          '0313038' : '1282',
          '0090477' : '1188',
          '0072471' : '1950',
          '1242441' : '712',
          '0756573' : '36',
          '1442109' : '740',
          '0771329' : '490',
          '2400129' : '2579',
          '0239195' : '389',
          '1197580' : '388',
          '2369037' : '2878',
          '0108819' : '819',
          '1181541' : '426',
          '1598876' : '1070',
          '0915414' : '287',
          '0088487' : '801',
          '2569792' : '3665',
          '1942919' : '2504',
          '1772752' : '1576',
          '0363328' : '1002',
          '0310952' : '808',
          '1837576' : '2381',
          '1567432' : '1618',
          '1561755' : '1299',
          '2938522' : '4105',
          '0106168' : '2118',
          '0290978' : '79',
          '1553656' : '3807',
          '0892700' : '391',
          '1470837' : '3486',
          '0446241' : '292',
          '0312098' : '563',
          '1741256' : '1798',
          '1000734' : '227',
          '0273028' : '795',
          '1466074' : '1629',
          '1319690' : '550',
          '1134000' : '2892',
          '0460693' : '1147',
          '1548850' : '689',
          '1856010' : '3103',
          '0376591' : '1266',
          '0072468' : '737',
          '2781552' : '3500',
          '1839417' : '2339',
          '2709648' : '3982',
          '0127402' : '1955',
          '2678354' : '3497',
          '2573338' : '4102',
          '0460627' : '28',
          '1266020' : '450',
          '1727387' : '2292',
          '0320000' : '1044',
          '2215797' : '3326',
          '2377271' : '3421',
          '0098833' : '2024',
          '0080231' : '2026',
          '0118421' : '14',
          '2293002' : '2743',
          '0090525' : '1156',
          '0441059' : '3785',
          '1720607' : '1117',
          '1167345' : '1474',
          '1748888' : '1613',
          '0108783' : '1838',
          '1255913' : '608',
          '2258904' : '3632',
          '2193021' : '3005',
          '1615602' : '1224',
          '0285403' : '24',
          '0121955' : '116',
          '1492088' : '1939',
          '0071075' : '596',
          '0086662' : '1438',
          '0862620' : '463',
          '0435576' : '510',
          '1388782' : '598',
          '1709198' : '1120',
          '2390334' : '3299',
          '0147746' : '1114',
          '1475269' : '1028',
          '0407384' : '1321',
          '2057856' : '2218',
          '2092588' : '2018',
          '0078607' : '147',
          '0847150' : '332',
          '1225901' : '344',
          '3202220' : '4000',
          '1178636' : '361',
          '1845307' : '1788',
          '1477188' : '1839',
          '0069655' : '3697',
          '1493923' : '1103',
          '0460671' : '588',
          '1722512' : '3056',
          '0187646' : '2006',
          '2318134' : '2741',
          '0403778' : '3826',
          '1974470' : '2155',
          '1459243' : '916',
          '2177489' : '2581',
          '1584150' : '797',
          '2078818' : '3061',
          '2355249' : '2795',
          '1956017' : '2807',
          '2526046' : '3507',
          '0118303' : '459',
          '0115355' : '732',
          '0358856' : '335',
          '0465353' : '247',
          '2071645' : '3232',
          '0346223' : '1196',
          '1588221' : '977',
          '0950721' : '124',
          '0302128' : '886',
          '0476916' : '969',
          '1458547' : '1005',
          '0108755' : '1315',
          '0496424' : '78',
          '2167393' : '3609',
          '1828246' : '2322',
          '0863046' : '320',
          '1315063' : '573',
          '0281432' : '103',
          '2087820' : '3025',
          '0462097' : '1683',
          '0972412' : '128',
          '0112047' : '2068',
          '0489598' : '642',
          '3063454' : '4054',
          '0207919' : '935',
          '1396401' : '778',
          '2244871' : '3684',
          '0057790' : '2113',
          '1861225' : '1432',
          '2364582' : '4010',
          '1161861' : '1684',
          '1360590' : '392',
          '0813715' : '2',
          '0071059' : '2895',
          '0274298' : '529',
          '0460686' : '1333',
          '0772139' : '113',
          '2184737' : '3222',
          '0090436' : '1970',
          '1470249' : '2463',
          '0423661' : '1322',
          '1877889' : '2929',
          '1138475' : '1268',
          '1361839' : '768',
          '0958611' : '299',
          '1442449' : '1314',
          '2245988' : '3440',
          '1567254' : '895',
          '1519931' : '981',
          '1442462' : '615',
          '1660055' : '990',
          '1783878' : '2383',
          '1235099' : '355',
          '0411011' : '483',
          '1079959' : '312',
          '1461312' : '707',
          '0066685' : '1338',
          '0883772' : '1032',
          '2346091' : '2141',
          '0106028' : '331',
          '2403529' : '2530',
          '1819654' : '1791',
          '0487831' : '43',
          '1235547' : '432',
          '1615919' : '1061',
          '1595680' : '1317',
          '1771072' : '2471',
          '0077000' : '802',
          '2006848' : '2550',
          '1548669' : '851',
          '1836417' : '1645',
          '2262456' : '2610',
          '0052451' : '1527',
          '0493093' : '448',
          '0092359' : '1129',
          '1622696' : '854',
          '0063897' : '2975',
          '0303461' : '195',
          '0081933' : '1761',
          '0272980' : '473',
          '0383153' : '224',
          '0888420' : '1443',
          '1336685' : '2512',
          '1442552' : '755',
          '2044128' : '3832',
          '1820742' : '1805',
          '2571542' : '3449',
          '0844441' : '366',
          '0488352' : '177',
          '0409572' : '1350',
          '0083413' : '2055',
          '2073664' : '2694',
          '1593823' : '1276',
          '1731601' : '2281',
          '1091909' : '533',
          '0395057' : '1355',
          '2330254' : '2839',
          '0892187' : '2674',
          '0859592' : '467',
          '1673792' : '962',
          '1935066' : '1696',
          '2211129' : '2860',
          '0112022' : '566',
          '1777391' : '1517',
          '0080240' : '91',
          '0460665' : '1326',
          '1415098' : '3003',
          '0111987' : '2148',
          '0103491' : '631',
          '1950799' : '2409',
          '0775349' : '492',
          '1717499' : '1331',
          '0075488' : '2060',
          '0950701' : '756',
          '0249327' : '2490',
          '0098901' : '2183',
          '1073507' : '436',
          '0318997' : '1457',
          '1375408' : '1818',
          '0380136' : '3905',
          '1441219' : '742',
          '1798274' : '1737',
          '0108872' : '268',
          '1769411' : '1211',
          '1960255' : '1650',
          '0118480' : '323',
          '0350448' : '3270',
          '0088621' : '1635',
          '1592270' : '933',
          '1626947' : '932',
          '0420416' : '892',
          '0460681' : '5',
          '1730535' : '1630',
          '0108967' : '893',
          '1409667' : '988',
          '0995832' : '413',
          '0319210' : '3642',
          '0213327' : '565',
          '0068527' : '811',
          '0324864' : '645',
          '0123360' : '4096',
          '0224853' : '1332',
          '2058303' : '1835',
          '0042114' : '1545',
          '1102770' : '3260',
          '1587394' : '1918',
          '2737290' : '4029',
          '0437745' : '61',
          '2299207' : '2841',
          '0169491' : '825',
          '1105711' : '1261',
          '1429534' : '1483',
          '2691732' : '3434',
          '0952665' : '133',
          '1865718' : '2613',
          '2958762' : '3989',
          '1288499' : '744',
          '1137462' : '430',
          '2564734' : '4062',
          '0167720' : '1034',
          '0108938' : '1464',
          '2596412' : '3306',
          '1663613' : '1957',
          '0318913' : '3416',
          '0071040' : '817',
          '0925266' : '101',
          '2237342' : '3281',
          '2763296' : '4161',
          '1397256' : '570',
          '2699374' : '3305',
          '1782352' : '1270',
          '0163507' : '796',
          '0377260' : '293',
          '0840979' : '514',
          '1635327' : '1462',
          '1971860' : '1794',
          '3039270' : '3846',
          '0175394' : '1221',
          '0165598' : '246',
          '1409055' : '858',
          '0240278' : '1115',
          '1733785' : '2425',
          '0452718' : '1577',
          '1789621' : '1213',
          '0175381' : '229',
          '0194608' : '1498',
          '0096569' : '920',
          '0129690' : '1330',
          '2548214' : '3916',
          '1701982' : '1932',
          '1197567' : '367',
          '1587000' : '1218',
          '1212452' : '2053',
          '0115317' : '3117',
          '0460637' : '48',
          '1971534' : '2332',
          '0801426' : '243',
          '2139371' : '2608',
          '0472954' : '255',
          '0759364' : '876',
          '0442632' : '2371',
          '0956036' : '298',
          '1468779' : '974',
          '1641653' : '881',
          '0283205' : '1082',
          '0370194' : '1819',
          '1405406' : '600',
          '0408403' : '1405',
          '0366028' : '1257',
          '1765622' : '1646',
          '0467742' : '2622',
          '1604113' : '1729',
          '0083466' : '232',
          '3093354' : '4139',
          '2761354' : '4116',
          '0063881' : '1445',
          '0287839' : '458',
          '2049323' : '2499',
          '1828238' : '1793',
          '2275990' : '2866',
          '0149460' : '482',
          '2266639' : '3183',
          '2356791' : '3962',
          '0106064' : '1402',
          '0830161' : '3707',
          '0086831' : '2927',
          '1597420' : '1025',
          '1836037' : '2536',
          '1183195' : '601',
          '1804880' : '1520',
          '2404043' : '2457',
          '0318236' : '2021',
          '3240572' : '4035',
          '0790603' : '163',
          '1841108' : '1595',
          '1587694' : '1280',
          '0411008' : '1',
          '0086827' : '3924',
          '1337578' : '773',
          '0421482' : '3834',
          '2443340' : '3327',
          '1979918' : '2643',
          '0098844' : '687',
          '0098882' : '1041',
          '1442566' : '1491',
          '0489606' : '115',
          '1802693' : '2853',
          '1591490' : '1069',
          '1608180' : '1059',
          '2359788' : '2850',
          '1382367' : '505',
          '0096694' : '704',
          '0103360' : '1110',
          '0876235' : '304',
          '1578873' : '880',
          '1024932' : '669',
          '0278251' : '1533',
          '0270594' : '1597',
          '1131751' : '919',
          '1743899' : '1203',
          '0098769' : '644',
          '1837855' : '2140',
          '0412253' : '32',
          '2343137' : '3233',
          '2261391' : '2951',
          '1819022' : '1396',
          '2088447' : '1947',
          '1489312' : '2273',
          '2204714' : '3220',
          '0380953' : '2659',
          '3012976' : '3894',
          '1363468' : '1458',
          '0086818' : '812',
          '0069654' : '2717',
          '0257315' : '1123',
          '0061266' : '1481',
          '1785123' : '3367',
          '1560591' : '2931',
          '1400819' : '1329',
          '2904568' : '4003',
          '0382501' : '412',
          '2063417' : '2353',
          '1663641' : '1386',
          '0483536' : '650',
          '0094511' : '2570',
          '0452573' : '441',
          '1708882' : '2228',
          '0347840' : '88',
          '1879713' : '2527',
          '2405378' : '3468',
          '1378167' : '617',
          '0149437' : '239',
          '0182576' : '130',
          '0094525' : '406',
          '2382598' : '4067',
          '1885537' : '1487',
          '0955346' : '131',
          '0202722' : '3956',
          '0106057' : '1253',
          '0096725' : '1465',
          '2455514' : '3928',
          '0758737' : '139',
          '0108757' : '53',
          '0138739' : '2634',
          '0203259' : '731',
          '1563697' : '1581',
          '0105646' : '4046',
          '1422182' : '1178',
          '2375858' : '2831',
          '0108778' : '182',
          '0460655' : '1128',
          '2384811' : '3249',
          '0423776' : '1039',
          '0237123' : '290',
          '0290983' : '4079',
          '0445114' : '211',
          '1420425' : '616',
          '1065309' : '1027',
          '0759475' : '179',
          '0814164' : '160',
          '1637727' : '27387',
          '2182229' : '2917',
          '1475582' : '1001',
          '1843230' : '1808',
          '2710394' : '4052',
          '2707792' : '4147'
         }