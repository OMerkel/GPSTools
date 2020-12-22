from xml.dom import minidom
import json
import urllib.request
import time
import sys

class Gpx:

  def __init__(self, file = '../gpx/W1-Waschenbach-Neutsch-Perlenkette.gpx'):
    self.doc = minidom.parse(file)
    self.trkElements = self.doc.getElementsByTagName('trk')
    # print(len(self.trkElements), 'tracks found')
    self.trks = []
    for trkElement in self.trkElements:
      nameElements = trkElement.getElementsByTagName('name')
      name = nameElements[0].firstChild.data
      trkSeg = trkElement.getElementsByTagName('trkseg')
      trkPts = trkElement.getElementsByTagName('trkpt')
      # print('Amount of trkPts in trk', name, ':', len(trkPts))
      trkPtList = []
      for trkPt in trkPts:
        lon = trkPt.attributes['lon'].value
        lat = trkPt.attributes['lat'].value
        trkPtData = { 'lon': lon, 'lat': lat }
        eleElement = trkPt.getElementsByTagName('ele')
        if len(eleElement) == 1:
          elevation = eleElement[0].firstChild.data
          trkPtData['ele'] = str(round(float(elevation),2))
        timeElement = trkPt.getElementsByTagName('time')
        if len(timeElement) == 1:
          time = timeElement[0].firstChild.data
          trkPtData['time'] = time
        trkPtList.append( trkPtData )
      self.trks.append( {'name': name, 'trkseg': trkPtList} )
    # print(self.trks)

  def trkGet(self, name):
    result = None
    for trk in self.trks:
      if trk['name'] == name and result == None:
        result = trk
        break
    return result

  def trkReverse(self, name):
    trk = self.trkGet(name)
    trk['trkseg'].reverse()

  def clearGpx(self):
    root = self.doc.documentElement
    while root.childNodes:
      root.removeChild(root.childNodes[0])

  def renderTrks(self):
    self.clearGpx()
    # print(self.doc.toxml())
    root = self.doc.documentElement
    for trk in self.trks:
      trkNameElement = self.doc.createElement('name')
      trkNameElement.appendChild(self.doc.createTextNode(trk['name']))
      trkSegElement = self.doc.createElement('trkseg')
      for trkPt in trk['trkseg']:
        trkPtElement = self.doc.createElement('trkpt')
        trkPtElement.setAttribute('lat' , trkPt['lat'])
        trkPtElement.setAttribute('lon' , trkPt['lon'])
        if 'ele' in trkPt:
          eleElement = self.doc.createElement('ele')
          eleElement.appendChild(self.doc.createTextNode(trkPt['ele']))
          trkPtElement.appendChild(eleElement)
        if 'time' in trkPt:
          timeElement = self.doc.createElement('time')
          timeElement.appendChild(self.doc.createTextNode(trkPt['time']))
          trkPtElement.appendChild(timeElement)
        trkSegElement.appendChild(trkPtElement)
      trkElement = self.doc.createElement('trk')
      trkElement.appendChild(trkNameElement)
      trkElement.appendChild(trkSegElement)
      root.appendChild(trkElement)
    print(self.doc.toprettyxml( indent='  ' ))

    """
      trkSeg.appendChild(gpxDoc.createTextNode('\n    '))
      trkSeg.appendChild(trkPt)
    trkSeg.appendChild(gpxDoc.createTextNode('\n  '))
    """

  def elevation(self, coords):
    # url = "https://maps.googleapis.com/maps/api/elevation/json"
    url = "https://api.opentopodata.org/v1/eudem25m"
    request = urllib.request.urlopen(url+"?locations="+str(coords))
    try:
      results = json.load(request).get('results')
      if 0 < len(results):
        return results
      else:
        print('HTTP GET Request failed.')
      print('JSON decode failed: ' + str(request))
    except e:
      pass

  def lookupElevation(self, amount=10):
    coords = ''
    n=amount
    for trk in self.trks:
      for trkpt in trk['trkseg']:
        if n>0 and not 'ele' in trkpt:
          if len(coords) > 0:
            coords += '|'
          coords += trkpt['lat'] + ',' + trkpt['lon']
          n -= 1
    eleList = self.elevation(coords)
    n=amount
    for trk in self.trks:
      for trkpt in trk['trkseg']:
        if n>0 and not 'ele' in trkpt:
          trkpt['ele'] = str(round(float(eleList[amount-n]['elevation']),2))
          n -= 1

if __name__ == "__main__":
  if len(sys.argv) == 1:
    filepath = '../gpx/W1-Waschenbach-Neutsch-Perlenkette.gpx'
  else:
    filepath = sys.argv[1]
  gpx = Gpx(file = filepath)
  # gpx.trkReverse('W1-Waschenbach-Neutsch-Perlenkette')
  gpx.lookupElevation(amount=80)
  gpx.renderTrks()
