// ==============================================================================
// OSM_AUDIT_2025: NDVI SPATIAL AUDIT
// Sentinel-2 NDVI 时序 + 对照区 + 敏感性分析
// ==============================================================================

// ⚠️ Update END_DATE before each run
var START_DATE = '2018-01-01';
var END_DATE   = '2026-03-15';  // <-- UPDATE ME

// 1. 审计区坐标
var shepperton = ee.Geometry.Point([-0.4640, 51.4065]); 
var analysisBuffer = shepperton.buffer(1000);

// 2. Sprawl Zone（新建停车场区域，对应 EIA 规划图 Zone C 中心）
var sprawlZone = ee.Geometry.Point([-0.469366, 51.410315]).buffer(100);

// 3. 对照区：Sunbury 方向未开发的稳定绿地（距 Shepperton ~2km，无大型开发）
var controlZone = ee.Geometry.Point([-0.4104592619093905, 51.40739479750269]).buffer(100);

// Sentinel-2
var sentinel2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterBounds(analysisBuffer)
  .filterDate(START_DATE, END_DATE)
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20));

var maskS2clouds = function(image) {
  // 1. 基本的 QA60 去云掩膜
  var qa = image.select('QA60');
  var maskQA = qa.bitwiseAnd(1 << 10).eq(0).and(qa.bitwiseAnd(1 << 11).eq(0));
  
  // 2. 增强型 SCL (Scene Classification Layer) 场景分类去云
  // 剔除：3(云影), 8(中概率云), 9(高概率云), 10(薄卷云), 11(雪/冰)
  var scl = image.select('SCL');
  var maskSCL = scl.neq(3).and(scl.neq(8)).and(scl.neq(9)).and(scl.neq(10)).and(scl.neq(11));
  
  // 结合两层掩膜
  var combinedMask = maskQA.and(maskSCL);
  return image.updateMask(combinedMask).divide(10000);
};

var ndviCollection = sentinel2.map(function(img) {
  var masked = maskS2clouds(img);
  var ndvi = masked.normalizedDifference(['B8', 'B4']).rename('NDVI');
  return masked.addBands(ndvi).copyProperties(img, ['system:time_start', 'system:index']);
}).select(['NDVI']);

// ==============================================================================
// 统一输出合并图表 (用于一键 CSV 导出)
// ==============================================================================
// 既然需要做长期时序分析对比，最好的办法是把所有区域合并成一个FeatureCollection多序列输出
var roiCollection = ee.FeatureCollection([
  ee.Feature(sprawlZone, {label: 'Sprawl_Zone_Core'}),
  ee.Feature(controlZone, {label: 'Control_Zone'})
]);

// 为了计算方差 (stdDev) 并导出宽表 (Wide Format)
var extractStats = function(image) {
  var stats = image.reduceRegions({
    collection: roiCollection,
    reducer: ee.Reducer.mean().combine({
      reducer2: ee.Reducer.stdDev(),
      sharedInputs: true
    }),
    scale: 10
  });
  
  // 安全提取：使用 filter + first，避免动态生成导致的属性类型丢失
  var sp = ee.Feature(stats.filter(ee.Filter.eq('label', 'Sprawl_Zone_Core')).first());
  var ct = ee.Feature(stats.filter(ee.Filter.eq('label', 'Control_Zone')).first());
  
  // 原生保留 system:time_start 防止图表 x 轴识别报错
  return ee.Feature(null, {
    'Sprawl_Zone_Core_mean': sp.get('mean'),
    'Sprawl_Zone_Core_std': sp.get('stdDev'),
    'Control_Zone_mean': ct.get('mean'),
    'Control_Zone_std': ct.get('stdDev')
  }).set('system:time_start', ee.Number(image.get('system:time_start')));
};

// 获得宽表 FeatureCollection，每张影像对应1行，包含所有区域的 mean 和 stdDev
var timeSeriesData = ndviCollection.map(extractStats);

var consolidatedChart = ui.Chart.feature.byFeature({
  features: timeSeriesData,
  xProperty: 'system:time_start',
  yProperties: [
    'Sprawl_Zone_Core_mean', 'Sprawl_Zone_Core_std', 
    'Control_Zone_mean', 'Control_Zone_std'
  ]
})
.setChartType('ScatterChart')
.setOptions({
  title: 'NDVI Analytics Extraction Ready (with UQ StdDev Wide-Format)',
  vAxis: {title: 'NDVI'},
  pointSize: 2,
  dataOpacity: 0.5
});

print("【ACTION REQUIRED】");
print("1. We now explicitly export WIDE-FORMAT telemetry including Pixel StdDev.");
print("2. Click the pop-out arrow in the top right of this chart -> Download CSV.");
print("3. MUST Save as: data/raw_telemetry/ee-chart_ndvi.csv");
print(consolidatedChart);

// ==============================================================================
// 损失图（2018基线 vs 近期）
// ==============================================================================
var baseline2018 = ndviCollection.filterDate('2018-01-01', '2019-01-01').mean();
var recent2026 = ndviCollection.filterDate('2025-09-01', END_DATE).mean();
var loss = baseline2018.subtract(recent2026).rename('NDVI_Loss');

Map.centerObject(shepperton, 15);
Map.addLayer(loss.clip(analysisBuffer), 
  {min:-0.3, max:0.3, palette:['darkgreen','green','white','red','darkred']}, 
  'NDVI Loss (Red=Decline)');
Map.addLayer(sprawlZone, {color: 'red'}, 'Sprawl Zone', true);
Map.addLayer(controlZone, {color: 'green'}, 'Control Zone', true);