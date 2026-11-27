"""Screenshots of QGIS for Chapter 21 (Getting to Know QGIS).

Runs inside QGIS (tested with QGIS 3.34 on Linux) under a virtual display:

    Xvfb :77 -screen 0 1440x900x24 &  DISPLAY=:77 openbox &
    DISPLAY=:77 qgis --nologo --code qgis_screenshots.py

with ONLY=<step names> to retake some shots. It expects nc.gpkg (layers
counties, cities, rivers in EPSG:32119, built from Natural Earth and the
county table in data/nc_counties_2025.csv) and nc_cities.csv in D, and
writes PNGs to D/shots/. Then run qgis_annotate.py to add callouts and copy
the shots to images/qgis/.
"""
import os, traceback
from qgis.core import *
from qgis.gui import *
from qgis.utils import iface
from qgis.PyQt.QtCore import QTimer, Qt, QPointF, QSizeF, QRectF
from qgis.PyQt.QtGui import QColor, QFont
from qgis.PyQt.QtWidgets import QApplication, QAction, QDialog, QWidget, QDockWidget, QLineEdit, QComboBox
D = '/tmp/claude-0/s/qg/'
G = D + 'nc.gpkg'
OUT = D + 'shots/'
ONLY = os.environ.get('ONLY', '')
mw = iface.mainWindow()
P = QgsProject.instance()
L = {}
steps = []
def step(fn):
    steps.append(fn); return fn
CROP = {'qgis-delimited-text': 'Data Source Manager', 'qgis-new-geopackage': 'New GeoPackage', 'qgis-attribute-table': 'Features Total', 'qgis-field-calculator': 'Field Calculator', 'qgis-symbology': 'Symbology', 'qgis-labels': 'Labels', 'qgis-buffer-dialog': 'Buffer'}
def grab(name, widget=None):
    iface.messageBar().clearWidgets()
    QApplication.processEvents()
    if widget is None:
        pm = QApplication.primaryScreen().grabWindow(0)
        if name in CROP:
            w = find(CROP[name])
            if w:
                g = w.frameGeometry(); pm = pm.copy(g)
        pm.save(OUT + name + '.png')
    else:
        widget.grab().save(OUT + name + '.png')
    print('SHOT', name, flush=True)
def close_dialogs():
    for w in QApplication.topLevelWidgets():
        if w is not mw and w.isVisible() and isinstance(w, QDialog):
            try: w.reject()
            except Exception: w.close()
import sip
def kids(d, cls):
    out=[]
    for w in d.findChildren(QWidget):
        if w.metaObject().className()==cls.__name__:
            out.append(sip.cast(w, cls))
    return out
def byname(d, name):
    for w in d.findChildren(QWidget):
        if w.objectName()==name: return w
def find(title):
    for w in QApplication.topLevelWidgets():
        if w.isVisible() and title.lower() in w.windowTitle().lower(): return w
    print('NOTFOUND', title, [w.windowTitle() for w in QApplication.topLevelWidgets() if w.isVisible()], flush=True)
def act(name):
    a = mw.findChild(QAction, name)
    if a is None: print('NOACTION', name, flush=True)
    else: a.trigger()

def load():
    mw.showMaximized()
    P.setCrs(QgsCoordinateReferenceSystem('EPSG:32119'))
    for n in ['counties', 'rivers', 'cities']:
        lyr = QgsVectorLayer(f'{G}|layername={n}', n, 'ogr')
        P.addMapLayer(lyr); L[n] = lyr
    c = L['counties']
    sym = QgsFillSymbol.createSimple({'color': '#e8eef2', 'outline_color': '#6b7b88', 'outline_width': '0.2'})
    c.setRenderer(QgsSingleSymbolRenderer(sym))
    L['rivers'].setRenderer(QgsSingleSymbolRenderer(QgsLineSymbol.createSimple({'color': '#3d7ab8', 'width': '0.5'})))
    L['cities'].setRenderer(QgsSingleSymbolRenderer(QgsMarkerSymbol.createSimple({'name': 'circle', 'color': '#c0392b', 'size': '2.6', 'outline_color': 'white'})))
    iface.mapCanvas().setExtent(c.extent().buffered(15000))
    iface.mapCanvas().refresh()
    pt = mw.findChild(QDockWidget, 'ProcessingToolbox')
    if pt: pt.show()

def graduated():
    c = L['counties']
    r = QgsGraduatedSymbolRenderer('density')
    r.setClassificationMethod(QgsApplication.classificationMethodRegistry().method('Jenks'))
    r.updateClasses(c, 5)
    ramp = QgsStyle.defaultStyle().colorRamp('Greens')
    rngs = r.ranges()
    print('RANGES', len(rngs), flush=True)
    for i, rg in enumerate(rngs):
        sym = QgsFillSymbol.createSimple({'color': ramp.color(i / (len(rngs) - 1)).name(), 'outline_color': '#ffffff', 'outline_width': '0.2'})
        r.updateRangeSymbol(i, sym)
        r.updateRangeLabel(i, f'{rg.lowerValue():,.0f} – {rg.upperValue():,.0f}')
    r.setSourceColorRamp(ramp.clone())
    fmt = r.labelFormat(); fmt.setPrecision(0); fmt.setTrimTrailingZeroes(True); r.setLabelFormat(fmt)
    c.setRenderer(r)
    c.triggerRepaint()
    L['_ramp'] = ramp

def labels():
    lyr = L['cities']
    s = QgsPalLayerSettings()
    s.fieldName = 'name'
    f = QgsTextFormat(); f.setFont(QFont('Open Sans')); f.setSize(8.5); f.setColor(QColor('#222222'))
    b = QgsTextBufferSettings(); b.setEnabled(True); b.setSize(0.8); b.setColor(QColor('white')); f.setBuffer(b)
    s.setFormat(f)
    s.placement = Qgis.LabelPlacement.OrderedPositionsAroundPoint
    lyr.setLabeling(QgsVectorLayerSimpleLabeling(s)); lyr.setLabelsEnabled(True)
    lyr.triggerRepaint()

@step
def interface():
    grab('qgis-interface')

@step
def dsm():
    def go():
        d = find('Data Source Manager')
        if d: QTimer.singleShot(300, lambda: fill(d))
    def fill(d):
        for w in kids(d, QgsFileWidget):
            if w.isVisible():
                w.setFilePath(D + 'nc_cities.csv')
        def more():
            for gb in kids(d, QgsCollapsibleGroupBox):
                if gb.objectName() in ('fileFormatGroupBox','recordOptionsGroupBox','layerSettingsGroupBox'): gb.setCollapsed(True)
                if gb.objectName()=='geometryDefinitionGroupBox': gb.setCollapsed(False)
            for n,v in (('cmbXField','longitude'),('cmbYField','latitude')):
                c=byname(d,n)
                if c: c.setCurrentIndex(c.findText(v))
            for w in kids(d, QgsProjectionSelectionWidget):
                if w.objectName()=='crsGeometry': w.setCrs(QgsCoordinateReferenceSystem('EPSG:4326'))
            QTimer.singleShot(1500, lambda: grab('qgis-delimited-text'))
        QTimer.singleShot(1500, more)
    QTimer.singleShot(1500, go)
    QTimer.singleShot(6000, close_dialogs)
    try: iface.openDataSourceManagerPage('delimitedtext')
    except Exception: traceback.print_exc(); act('mActionDataSourceManager')
    return 7000

@step
def newgpkg():
    def fill():
        d = find('New GeoPackage Layer')
        if not d: return
        for fw in kids(d, QgsFileWidget): fw.setFilePath(D + 'field_sites.gpkg')
        tn = d.findChild(QLineEdit, 'mTableNameEdit')
        if tn: tn.setText('field_sites')
        gt = d.findChild(QComboBox, 'mGeometryTypeBox')
        if gt:
            for i in range(gt.count()):
                if gt.itemText(i) == 'Point': gt.setCurrentIndex(i)
        fn = d.findChild(QLineEdit, 'mFieldNameEdit')
        add = byname(d, 'mAddAttributeButton')
        print('ADD', add, flush=True)
        for nm in ('site_name','notes'):
            fn.setText(nm)
            if add: add.click()
        fn.setText('visit_date')
        ty = byname(d, 'mFieldTypeBox')
        if ty:
            for i in range(ty.count()):
                if ty.itemText(i).startswith('Date'): ty.setCurrentIndex(i); break
        for cr in kids(d, QgsProjectionSelectionWidget): cr.setCrs(QgsCoordinateReferenceSystem('EPSG:32119'))
        QTimer.singleShot(1200, lambda: grab('qgis-new-geopackage'))
    QTimer.singleShot(1500, fill)
    QTimer.singleShot(4500, close_dialogs)
    act('mActionNewGeoPackageLayer')
    return 1000

@step
def digitize():
    lyr = QgsVectorLayer('Point?crs=EPSG:32119&field=fid:integer&field=site_name:string(40)&field=visit_date:date&field=notes:string(100)', 'field_sites', 'memory')
    P.addMapLayer(lyr); L['sites'] = lyr
    iface.setActiveLayer(lyr)
    lyr.startEditing()
    # existing sites
    pts = [(560000, 245000, 'Eno River'), (600000, 225000, 'Jordan Lake'), (585000, 260000, 'Falls Lake')]
    import datetime
    from qgis.PyQt.QtCore import QDate
    for i, (x, y, n) in enumerate(pts):
        f = QgsFeature(lyr.fields()); f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x, y)))
        f['fid'] = i + 1; f['site_name'] = n; f['visit_date'] = QDate(2026, 9, 10 + i); f['notes'] = ''
        lyr.addFeature(f)
    lyr.setRenderer(QgsSingleSymbolRenderer(QgsMarkerSymbol.createSimple({'name': 'star', 'color': '#f1c40f', 'size': '5', 'outline_color': '#333333'})))
    iface.mapCanvas().setExtent(QgsRectangle(520000, 200000, 650000, 285000))
    act('mActionAddFeature')
    def form():
        f = QgsFeature(lyr.fields()); f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(575000, 238000)))
        f['site_name'] = 'New Hope Creek'; f['visit_date'] = QDate(2026, 9, 27); f['notes'] = 'Water sample, low flow'
        dlg = iface.getFeatureForm(lyr, f)
        dlg.setMode(QgsAttributeEditorContext.AddFeatureMode)
        dlg.show()
        dlg.move(int(mw.width() * 0.55), 220)
        for le in dlg.findChildren(QLineEdit): le.setCursorPosition(0)
        vm = QgsVertexMarker(iface.mapCanvas()); vm.setCenter(QgsPointXY(575000, 238000))
        vm.setIconType(QgsVertexMarker.ICON_CROSS); vm.setColor(QColor('#d62728')); vm.setIconSize(18); vm.setPenWidth(3)
        L['vm'] = vm
        QTimer.singleShot(1500, lambda: grab('qgis-digitize'))
    QTimer.singleShot(2500, form)
    return 6000

@step
def table():
    iface.mapCanvas().setExtent(L['counties'].extent().buffered(15000))
    iface.setActiveLayer(L['counties'])
    dlg = iface.showAttributeTable(L['counties'])
    dlg.resize(1100, 560); dlg.move(170, 160)
    QTimer.singleShot(800, lambda: (dlg.window().resize(690, 437), print('WIN', type(dlg.window()).__name__, dlg.window().size(), flush=True)))
    QTimer.singleShot(2200, lambda: grab('qgis-attribute-table', dlg.window()))
    def calc():
        a = [x for x in dlg.findChildren(QAction) if x.objectName() == 'mActionOpenFieldCalculator']
        def g2():
            d = find('Field Calculator')
            if d:
                ln = d.findChild(QLineEdit, 'mOutputFieldNameLineEdit')
                if ln: ln.setText('pop_per_km2')
                d.resize(1000, 760); d.move(200, 70)
                for ed in kids(d, QgsExpressionBuilderWidget): ed.setExpressionText('"pop_2025" / ("aland_sqmi" * 2.58999)')
                ty = byname(d, 'mOutputFieldTypeComboBox')
                if ty:
                    for i in range(ty.count()):
                        if 'Decimal' in ty.itemText(i): ty.setCurrentIndex(i); break
                QTimer.singleShot(1500, lambda: grab('qgis-field-calculator'))
            else:
                print('NOFCDLG', [type(w).__name__ for w in QApplication.topLevelWidgets() if w.isVisible()], flush=True)
        QTimer.singleShot(1500, g2)
        QTimer.singleShot(4000, close_dialogs)
        if a: a[0].trigger()
        else: print('NOCALC', flush=True)
    QTimer.singleShot(3500, calc)
    return 8000

@step
def symbology():
    graduated()
    iface.showLayerProperties(L['counties'], 'mOptsPage_Symbology')
    return 0  # blocking exec; handled by timer before call

@step
def labeling():
    labels()
    iface.showLayerProperties(L['cities'], 'mOptsPage_Labels')
    return 0

@step
def mapview():
    graduated(); labels()
    for n in ('counties', 'cities', 'rivers'):
        L[n].triggerRepaint()
    QTimer.singleShot(3000, lambda: grab('qgis-styled-map'))
    return 4500

@step
def buffer():
    import processing
    from processing.gui.AlgorithmDialog import AlgorithmDialog
    dlg = processing.createAlgorithmDialog('native:buffer', {'INPUT': L['rivers'].id(), 'DISTANCE': 5000, 'DISSOLVE': True})
    dlg.show(); dlg.resize(900, 640); dlg.move(260, 120)
    QTimer.singleShot(2500, lambda: grab('qgis-buffer-dialog'))
    return 4000

@step
def layout():
    graduated(); labels()
    lm = P.layoutManager()
    lay = QgsPrintLayout(P); lay.initializeDefaults(); lay.setName('NC population density')
    pg = lay.pageCollection().page(0); pg.setPageSize('Letter', QgsLayoutItemPage.Landscape)
    m = QgsLayoutItemMap(lay); m.setRect(20, 20, 20, 20)
    m.attemptMove(QgsLayoutPoint(10, 28, QgsUnitTypes.LayoutMillimeters))
    m.attemptResize(QgsLayoutSize(259, 140, QgsUnitTypes.LayoutMillimeters))
    m.setLayers([L['cities'], L['rivers'], L['counties']])
    m.setExtent(L['counties'].extent().buffered(30000))
    m.setFrameEnabled(True)
    lay.addLayoutItem(m)
    t = QgsLayoutItemLabel(lay); t.setText('Population Density of North Carolina Counties, 2025')
    tf = QgsTextFormat(); tf.setFont(QFont('Open Sans', 20, QFont.Bold)); tf.setSize(20); t.setTextFormat(tf)
    lay.addLayoutItem(t); t.attemptResize(QgsLayoutSize(259, 12, QgsUnitTypes.LayoutMillimeters)); t.attemptMove(QgsLayoutPoint(10, 10, QgsUnitTypes.LayoutMillimeters))
    lg = QgsLayoutItemLegend(lay); lg.setLinkedMap(m); lg.setTitle('People per sq. mi.')
    lg.setAutoUpdateModel(False)
    root = lg.model().rootGroup()
    for n in ('cities', 'rivers'):
        nd = root.findLayer(L[n].id())
        if nd: root.removeChildNode(nd)
    nd = root.findLayer(L['counties'].id())
    if nd: QgsLegendRenderer.setNodeLegendStyle(nd, QgsLegendStyle.Hidden)
    lg.updateLegend()
    lay.addLayoutItem(lg); lg.attemptMove(QgsLayoutPoint(14, 105, QgsUnitTypes.LayoutMillimeters))
    lg.setBackgroundColor(QColor(255, 255, 255, 220))
    sb = QgsLayoutItemScaleBar(lay); sb.setStyle('Single Box'); sb.setLinkedMap(m)
    sb.setUnits(QgsUnitTypes.DistanceMiles); sb.setNumberOfSegments(4); sb.setNumberOfSegmentsLeft(0); sb.setUnitsPerSegment(25); sb.setUnitLabel('mi')
    lay.addLayoutItem(sb); sb.attemptMove(QgsLayoutPoint(180, 150, QgsUnitTypes.LayoutMillimeters))
    na = QgsLayoutItemPicture(lay)
    na.setPicturePath(QgsApplication.svgPaths()[0] + 'arrows/NorthArrow_02.svg')
    lay.addLayoutItem(na); na.attemptResize(QgsLayoutSize(12, 18, QgsUnitTypes.LayoutMillimeters)); na.attemptMove(QgsLayoutPoint(255, 32, QgsUnitTypes.LayoutMillimeters))
    src = QgsLayoutItemLabel(lay); src.setText('Data: U.S. Census Bureau, 2025 population estimates; Natural Earth. Map: GEOG 370.')
    sf = QgsTextFormat(); sf.setFont(QFont('Open Sans', 8)); sf.setSize(8); src.setTextFormat(sf)
    src.adjustSizeToText(); lay.addLayoutItem(src); src.attemptMove(QgsLayoutPoint(10, 172, QgsUnitTypes.LayoutMillimeters))
    pg.setPageSize(QgsLayoutSize(279.4, 185, QgsUnitTypes.LayoutMillimeters))
    lm.addLayout(lay)
    ex = QgsLayoutExporter(lay)
    s = QgsLayoutExporter.ImageExportSettings(); s.dpi = 150
    print('EXPORT', ex.exportToImage(OUT + 'qgis-final-map.png', s), flush=True)
    des = iface.openLayoutDesigner(lay)
    des.window().showMaximized()
    QTimer.singleShot(4000, lambda: grab('qgis-print-layout'))
    return 6000

def run(i=0):
    if i >= len(steps):
        P.write(D + 'nc.qgz')
        QTimer.singleShot(500, QApplication.quit); return
    fn = steps[i]
    close_dialogs()
    if ONLY and fn.__name__ not in ONLY.split(','):
        QTimer.singleShot(10, lambda: run(i + 1)); return
    print('STEP', fn.__name__, flush=True)
    if fn.__name__ in ('symbology', 'labeling'):
        name = 'qgis-symbology' if fn.__name__ == 'symbology' else 'qgis-labels'
        def g():
            d = [w for w in QApplication.topLevelWidgets() if w.isVisible() and isinstance(w, QDialog)]
            if d:
                d[0].resize(1100, 720); d[0].move(170, 90)
            QTimer.singleShot(1500, lambda: (grab(name), [x.reject() for x in d]))
        QTimer.singleShot(2500, g)
        try: fn()
        except Exception: traceback.print_exc()
        QTimer.singleShot(500, lambda: run(i + 1)); return
    try:
        wait = fn() or 3000
    except Exception:
        traceback.print_exc(); wait = 500
    QTimer.singleShot(wait, lambda: run(i + 1))

def start():
    try: load()
    except Exception: traceback.print_exc()
    QTimer.singleShot(4000, run)
QTimer.singleShot(4000, start)
