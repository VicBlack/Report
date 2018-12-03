# encoding: utf-8
import re


class report:
    type = ""
    name = ""
    publisher = ""
    starttime = ""
    endtime = ""
    location = ""
    maxnum = ""
    availablenum = ""
    host = ""
    startjiontime = ""
    endjiontime = ""
    joinway = ""
    target = ""
    cancel = ""
    rethinking = ""


def DecodeReport(table):
    reports_pattern = re.compile('<tr (.*?)</tr>', re.DOTALL)
    reports = re.findall(reports_pattern, table)[1:]
    num_pattern = re.compile('<td align=\"center\" style=\"width:40px;\">([0-9]+)</td>')
    time_pattern = re.compile('(\d{4}/\d{1,2}/\d{1,2} \d{1,2}:\d{1,2}:\d{1,2})')
    location_pattern = re.compile('<td align="center" style="width:150px;">(.*?)</td>')
    typeway_pattern = re.compile('<td align="center" style="width:30px;">(.*?)</td>')
    nhp_pattern = re.compile('<td align=\"center\">(.*?)</td>')
    target_pattern = re.compile('href=\"javascript:__doPostBack\(&#39;(dg.*3)&#39;,&#39;')
    Reports = []
    for i in range(len(reports)):
        num = re.findall(num_pattern, reports[i])
        times = re.findall(time_pattern, reports[i])
        locationinfo = re.findall(location_pattern, reports[i])
        typewayinfo = re.findall(typeway_pattern, reports[i])
        nhp = re.findall(nhp_pattern, reports[i])
        target = re.findall(target_pattern, reports[i])
        areport = report()
        areport.maxnum = num[0]
        areport.availablenum = num[1]
        areport.starttime = times[0]
        areport.endtime = times[1]
        if len(times) > 2:
            areport.startjiontime = times[2]
            areport.endjiontime = times[3]
        areport.type = "".join(typewayinfo[0])
        areport.name = "".join(nhp[0])
        areport.publisher = "".join(nhp[1])
        areport.location = "".join(locationinfo[0])
        if nhp[2] != '&nbsp;':
            areport.host = "".join(nhp[2])
        areport.joinway = "".join(typewayinfo[1])
        areport.target = "".join(target[0])
        Reports.append(areport)
    return Reports


def DecodeCatchedReport(table):
    reports_pattern = re.compile('<tr nowrap=\"nowrap\"(.*?)</tr>', re.DOTALL)
    reports = re.findall(reports_pattern, table)
    num_pattern = re.compile('<td align=\"center\" style=\"width:40px;\">([0-9]+)</td>')
    time_pattern = re.compile('(\d{4}/\d{1,2}/\d{1,2} \d{1,2}:\d{1,2}:\d{1,2})')
    location_pattern = re.compile('<td align="center" style="width:150px;">(.*?)</td>')
    typeway_pattern = re.compile('<td align="center" style="width:30px;">(.*?)</td>')
    nhp_pattern = re.compile('<td align=\"center\">(.*?)</td>')
    out_pattern = re.compile('return confirm')
    cancel_pattern = re.compile('href=\"javascript:__doPostBack\(&#39;(dg.*1)&#39;,&#39;')
    rethinking_pattern = re.compile('href=\"javascript:__doPostBack\(&#39;(dg.*2)&#39;,&#39;')
    Reports = []
    for i in range(len(reports)):
        isout = re.findall(out_pattern, reports[i])
        if len(isout) > 0:
            num = re.findall(num_pattern, reports[i])
            times = re.findall(time_pattern, reports[i])
            locationinfo = re.findall(location_pattern, reports[i])
            typewayinfo = re.findall(typeway_pattern, reports[i])
            nhp = re.findall(nhp_pattern, reports[i])
            cancel = re.findall(cancel_pattern, reports[i])
            rethinking = re.findall(rethinking_pattern, reports[i])
            areport = report()
            areport.maxnum = num[0]
            areport.starttime = times[0]
            areport.endtime = times[1]
            if len(times) > 2:
                areport.startjiontime = times[2]
                areport.endjiontime = times[3]
            areport.type = "".join(typewayinfo[0])
            areport.name = "".join(nhp[0])
            areport.publisher = "".join(nhp[1])
            areport.location = "".join(locationinfo[0])
            if nhp[2] != '&nbsp;':
                areport.host = "".join(nhp[2])
            areport.joinway = "".join(typewayinfo[1])
            areport.cancel = "".join(cancel[0])
            areport.rethinking = "".join(rethinking[0])
            Reports.append(areport)
    return Reports