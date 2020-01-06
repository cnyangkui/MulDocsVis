import * as d3 from "d3"
import _ from "lodash"
import longdisHighsimilarity from "./dist2similarity.js";
import Graph from "./dijkstra.js";

/**
 * 获取投影数据的范围
 * @param {Array} projdata [{index: number, text: string, x: number, y: number}, ...]
 * @returns {Object} {
 *  dataExtent: Array [minx, miny, maxx, maxy]
 *  mapExtent: Array [minx, miny, maxx, maxy]
 * }
 */
function getExtent(projdata) {
  let xExt = d3.extent(projdata, d => d.x);
  let yExt = d3.extent(projdata, d => d.y);
  let x = xExt[1] - xExt[0] > yExt[1] - yExt[0] ? xExt : yExt;
  let y = xExt[1] - xExt[0] < yExt[1] - yExt[0] ? xExt : yExt;
  let dataExtent = [x[0], y[0], x[1], y[1]];
  let mapExtent = [
    x[0] - 0.1 * (x[1] - x[0]),
    y[0] - 0.1 * (y[1] - y[0]),
    x[1] + 0.1 * (x[1] - x[0]),
    y[1] + 0.1 * (y[1] - y[0])
  ];
  return {
    dataExtent: dataExtent,
    mapExtent: mapExtent
  };
}

/**
 * 在投影数据四周生成随机点
 * @param {Array} dataExtent [minx, miny, maxx, maxy]
 * @param {Array} mapExtent [minx, miny, maxx, maxy]
 * @param {number} pointNum int
 * @returns Array 数组中每个元素是一个坐标 [x, y]
 */
function generateOuterPoints(dataExtent, mapExtent, pointNum) {
  let outerPoints = [];
  for (let i = 0; i < pointNum; i++) {
    let tmp = i % 4;
    if (tmp == 0) {
      let x = _.random(mapExtent[0], dataExtent[2], true);
      let y = _.random(mapExtent[1], dataExtent[1], true);
      outerPoints.push([x, y]);
    } else if (tmp == 1) {
      let x = _.random(dataExtent[2], mapExtent[2], true);
      let y = _.random(mapExtent[1], dataExtent[3], true);
      outerPoints.push([x, y]);
    } else if (tmp == 2) {
      let x = _.random(dataExtent[0], mapExtent[2], true);
      let y = _.random(dataExtent[3], mapExtent[3], true);
      outerPoints.push([x, y]);
    } else {
      let x = _.random(mapExtent[0], dataExtent[0], true);
      let y = _.random(dataExtent[1], mapExtent[3], true);
      outerPoints.push([x, y]);
    }
  }
  return outerPoints;
}

/**
 * 在投影数据中点稀疏处生成随机点
 * @param {Array} projdata [{index: number, text: string, x: number, y: number}, ...]
 * @param {Array} dataExtent [minx, miny, maxx, maxy]
 * @param {number} innerXNum int
 * @param {number} innerYNum int
 * @returns {Array} 数组中每个元素是一个坐标 [x, y]
 */
function generateInnerPoints(projdata, dataExtent, innerXNum, innerYNum) {
  let innerPoints = [];
  let xspan =
    (dataExtent[2] - dataExtent[0]) / innerXNum;
  let yspan =
    (dataExtent[3] - dataExtent[1]) / innerYNum;
  let xScale = d3
    .scaleQuantize()
    .domain([dataExtent[0], dataExtent[2]])
    .range(d3.range(0, innerXNum));
  let yScale = d3
    .scaleQuantize()
    .domain([dataExtent[1], dataExtent[3]])
    .range(d3.range(0, innerYNum));
  let grid = [];
  for (let i = 0; i < innerXNum; i++) {
    let row = [];
    for (let j = 0; j < innerYNum; j++) {
      row.push(0);
    }
    grid.push(row);
  }
  for (let i = 0, len = projdata.length; i < len; i++) {
    let x = xScale(projdata[i].x);
    let y = yScale(projdata[i].y);
    grid[x][y]++;
  }
  for (let i = 0; i < innerXNum; i++) {
    for (let j = 0; j < innerYNum; j++) {
      if (grid[i][j] < 10) {
        let diff = 10 - grid[i][j];
        while (diff > 0) {
          let x =
            dataExtent[0] + _.random(i * xspan, (i + 1) * xspan, true);
          let y =
            dataExtent[1] + _.random(j * yspan, (j + 1) * yspan, true);
          innerPoints.push([x, y]);
          diff--;
        }
      }
    }
  }
  return innerPoints;
}

/**
 * Voronoi 迭代，生成地图
 * @param {Array} mapExtent [minx, miny, maxx, maxy]
 * @param {Array} allPoints 数组中每个元素是一个坐标 [x, y]
 * @param {number} mapIterationNum int, 迭代次数
 * @returns {Array} 数组中每一个元素表示一个多边形
 */
function getVoronoi(mapExtent, allPoints, mapIterationNum) {
  let cells = d3
    .voronoi()
    .extent([
      [mapExtent[0], mapExtent[1]],
      [mapExtent[2], mapExtent[3]]
    ])
    .polygons(allPoints);
  // 获得Voronoi的多边形
  let polygons = cells.map(c => {
    let pg = c;
    pg.push(c[0]);
    return pg;
  });
  // Voronoi每次选取多边形中心，重新绘制，多次迭代后网格趋向于六边形
  let centerPoints = [];
  for (let i = 0; i < mapIterationNum; i++) {
    centerPoints = polygons.map(d => d3.polygonCentroid(d));
    cells = d3
      .voronoi()
      .extent([
        [mapExtent[0], mapExtent[1]],
        [mapExtent[2], mapExtent[3]]
      ])
      .polygons(centerPoints);
    polygons = cells.map(c => {
      let pg = c;
      pg.push(c[0]);
      return pg;
    });
  }
  return polygons;
}

/**
 * 为所有多边形边上的点
 * @param {Array} polygons 数组中每个元素是一个多边形，表现为一系列坐标的集合
 * @param {Object} pointIndexInfo {dataPoint: [0, a], outerPoint: [a, b], innerPoint: [b, c]}
 * @returns {Object} {ecoords:Array, ecoords2index: Map, edge2docindex: Map}. ecoords存储多边形上的顶点坐标, ecoords2index存储 <多边形顶点坐标, 顶点索引> 的映射, edges存储 <边,共边多边形索引> 的映射.
 */
function getAllEdges(polygons, pointIndexInfo) {
  let ecoords2index = new Map();
  let ecoords = [];
  let edge2docindex = new Map();
  let p_index = 0;
  // 构建多边形边上点的坐标与索引的互相映射
  for (let pi in polygons) {
    if (pi >= pointIndexInfo.outerPoint[0] && pi < pointIndexInfo.outerPoint[1]) {
      continue;
    }
    polygons[pi].forEach((point) => {
      ecoords2index.set(JSON.stringify(point), p_index);
      ecoords[p_index] = point;
      p_index++;
    });
  }
  // 对于多边形的每条边，获得与之共边的多边形的索引
  for (let pi in polygons) {
    if (pi >= pointIndexInfo.outerPoint[0] && pi < pointIndexInfo.outerPoint[1]) {
      continue;
    }
    let pg = polygons[pi];
    for (let i = 0, len = pg.length - 1; i < len; i++) {
      let p1 = pg[i]; // 多边形上的节点
      let p2 = pg[i + 1]; // 多边形上的节点
      let i1 = ecoords2index.get(JSON.stringify(p1));
      let i2 = ecoords2index.get(JSON.stringify(p2));
      let edge1 = i1 + "-" + i2;
      let edge2 = i2 + "-" + i1;
      if (edge2docindex.has(edge1)) {
        let value = edge2docindex.get(edge1);
        value.push(pi);
        edge2docindex.set(edge1, value);
      } else {
        edge2docindex.set(edge1, [pi]);
      }
      if (edge2docindex.has(edge2)) {
        let value = edge2docindex.get(edge2);
        value.push(pi);
        edge2docindex.set(edge2, value);
      } else {
        edge2docindex.set(edge2, [pi]);
      }
    }
  };
  return {
    ecoords,
    ecoords2index,
    edge2docindex
  };
}

/**
 * 获得图结构数据
 * @param {Array} similarityMatrix 二维数组, 存储所有文档对的相似度 
 * @param {Map} edge2docindex <边, 共边多边形的索引> 
 * @param {Array} ecoords 数组每一个元素是多边形的一个顶点坐标 
 * @param {Object} pointIndexInfo {dataPoint: [0, a], outerPoint: [a, b], innerPoint: [b, c]}
 * @returns {Map} 表现为 <source1, {target1: weight1, target2: weight2}>
 */
function getGraphData(similarityMatrix, edge2docindex, ecoords, pointIndexInfo) {
  // 多边形每条边距离的归一化
  let weightlist = [];
  for (let [edge, docindex] of edge2docindex) {
    let [p1, p2] = edge.split("-");
    let weight = 0;
    if (docindex.length == 2) {
      let c1 = ecoords[parseInt(p1)];
      let c2 = ecoords[parseInt(p2)];
      weight = Math.sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2); // 2D 欧式距离作为边权重
      weightlist.push(weight);
    }
  }
  let max = d3.max(weightlist);
  let weightScale = d3
    .scaleLinear()
    .domain([0, max])
    .range([0, 1]);
  // 计算多边形每条边上的权值，根据文档相似度赋予，从而构造图数据
  let graphdata = new Map();
  for (let [edge, docindex] of edge2docindex) {
    let [p1, p2] = edge.split("-");
    let weight = 0;
    if (docindex.length == 2) {
      let c1 = ecoords[parseInt(p1)];
      let c2 = ecoords[parseInt(p2)];
      if (docindex[0] < pointIndexInfo.dataPoint[1] && docindex[1] < pointIndexInfo.dataPoint[1]) {
        // weight = similarityMatrix[docindex[0]][docindex[1]]; // 相似度作为边权重
        // weight = Math.sqrt((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2) // 2D 欧式距离作为边权重
        weight =
          weightScale(Math.sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2)) * 0.3
          + similarityMatrix[docindex[0]][docindex[1]] * 0.7;
      } else {
        weight = 1;
      }
    } else if (docindex.length == 1) {
      weight = 1 / 0;
    }
    if (graphdata.has(p1)) {
      // 图数据中是否有起点为p1的数据
      let target = graphdata.get(p1); //起点为p1的数据的终点
      target[p2] = weight; // 加入一个新的终点
      graphdata.set(p1, target);
    } else {
      let target = {};
      target[p2] = weight;
      graphdata.set(p1, target);
    }
  }
  return graphdata;
}

/**
 * 转换聚类数据格式
 * @param {Object} clusterdata {label1: [index1, index2, ...], label2: [...], ...}
 * @returns {Object} {index: label, ...} index 和 label 都为 int 类型
 */
function getCluster(clusterdata) {
  let cluster = {};
  Object.keys(clusterdata).forEach(key => {
    clusterdata[key].forEach(value => {
      cluster[value] = +key;
    })
  })
  return cluster;
}

/**
 * 计算最短路径
 * @param {Array} projdata [{index: number, text: string, x: number, y: number}, ...]
 * @param {Array} similarityMatrix 二维数组, 存储所有文档对的相似度 
 * @param {number} dist_quantile 距离分位数阈值, 过滤获得距离大于该分位数的文档对
 * @param {number} similarity_threshold 相似度阈值, 过滤获得相似度大于该值的文档对
 * @param {Map} graphdata 图结构数据, 表现为 <source1, {target1: weight1, target2: weight2}>
 * @param {Array} polygons 数组中每个元素是一个多边形，表现为一系列坐标的集合
 * @param {Array} ecoords 存储多边形上的顶点坐标
 * @param {Map} ecoords2index 存储 <多边形顶点坐标, 顶点索引> 的映射
 * @returns {Map} <pair, path> pair是一个文档索引对，paths是一个数组，表示一条路劲，每一条路径是一组坐标的集合
 */
function shortestPath(projdata, similarityMatrix, dist_quantile = 0.3, similarity_threshold = 0.2, graphdata, polygons, ecoords, ecoords2index) {
  // 构造Graph
  let graph = new Graph();
  let paths = new Map();
  for (let [key, value] of graphdata) {
    graph.addVertex(key, value);
  }
  longdisHighsimilarity(projdata, similarityMatrix, dist_quantile, similarity_threshold).forEach(d => {
    let pair = d.pair.split("-");
    let pg1 = polygons[parseInt(pair[0])];
    let pg2 = polygons[parseInt(pair[1])];
    let distance = 1 / 0;
    let start = pg1[0],
      end = pg2[0];
    for (let i = 0, len1 = pg1.length; i < len1; i++) {
      for (let j = 0, len2 = pg2.length; j < len2; j++) {
        let p1 = pg1[i];
        let p2 = pg2[j];
        let tmp = Math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2);
        if (tmp < distance) {
          distance = tmp;
          start = p1;
          end = p2;
        }
      }
    }
    let startIndex = ecoords2index.get(JSON.stringify(start));
    let endIndex = ecoords2index.get(JSON.stringify(end));
    let pathstr = graph
      .shortestPath(startIndex + "", endIndex + "")
      .concat([startIndex + ""])
      .reverse();
    let pathcoords = [];
    pathcoords.push(pg1.data);
    pathstr.forEach(pid => {
      pathcoords.push(ecoords[parseInt(pid)]);
    });
    pathcoords.push(pg2.data);
    paths.set(pair, pathcoords)
  })
  return paths;
}

/**
 * 计算得到地图相关数据
 * @param {Array} projdata [{index: number, text: string, x: number, y: number}, ...]
 * @param {Array} similarityMatrix 二维数组, 存储所有文档对的相似度 
 * @param {Object} clusterdata {label1: [index1, index2, ...], label2: [...], ...}
 * @param {Object} config {
 *  mapIterationNum: number 地图迭代次数
 *  outerPointNum: number 四周随机点数量
 *  innerXNum: number 投影数据网格划分，一行划分的数量
 *  innerYNum: number 投影数据网格划分，一列划分的数量
 *  dist_quantile: number 距离分位数
 *  similarity_threshold: number 相似度阈值
 * }
 * @returns {Object} {dataExtent: Array, mapExtent: Array, allPoints: Array, pointIndexInfo: Object, polygons: Array, ecoords: Array, ecoords2index: Map, edge2docindex: Map, paths: Array, clusters: Object }
 */
function processMapData(projdata, similarityMatrix, clusterdata, config) {
  let { dataExtent, mapExtent } = getExtent(projdata);
  let outerPoints = generateOuterPoints(dataExtent, mapExtent, config.outerPointNum);
  let innerPoints = generateInnerPoints(projdata, dataExtent, config.innerXNum, config.innerYNum);
  let allPoints = projdata.map(d => [d.x, d.y]).concat(outerPoints).concat(innerPoints);
  let pointIndexInfo = {
    dataPoint: [0, projdata.length],
    outerPoint: [projdata.length, projdata.length + outerPoints.length],
    innerPoint: [projdata.length + outerPoints.length, allPoints.length]
  };
  let polygons = getVoronoi(mapExtent, allPoints, config.mapIterationNum);
  let clusters = getCluster(clusterdata);
  let { ecoords, ecoords2index, edge2docindex } = getAllEdges(polygons, pointIndexInfo);
  let graphdata = getGraphData(similarityMatrix, edge2docindex, ecoords, pointIndexInfo)
  let paths = shortestPath(projdata, similarityMatrix, config.dist_quantile, config.similarity_threshold, graphdata, polygons, ecoords, ecoords2index);
  return { dataExtent, mapExtent, allPoints, pointIndexInfo, polygons, ecoords, ecoords2index, edge2docindex, paths, clusters }
}

export default processMapData;