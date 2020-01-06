<template>
  <div class="fastmap-container">
    <div id="fastmap"></div>
  </div>
</template>

<script>
import * as _ from "lodash";
import * as d3 from "d3";
import { Map as ol_Map, View as ol_View, Feature as ol_Feature } from "ol";
import { Group as ollayer_Group, Vector as ollayer_Vector } from "ol/layer";
import { Vector as olsource_Vector } from "ol/source";
import { getCenter as olextent_getCenter } from "ol/extent";
import { Projection as olproj_Projection } from "ol/proj";
import {
  Point as olgeom_Point,
  Polygon as olgeom_Polygon,
  LineString as olgeom_LineString
} from "ol/geom";
import {
  Circle as olstyle_Circle,
  Text as olstyle_Text,
  Style as olstyle_Style,
  Fill as olstyle_Fill,
  Stroke as olstyle_Stroke
} from "ol/style";
import { Select as olinteraction_Select } from "ol/interaction";
import {
  defaults as olcontrol_defaults,
  OverviewMap as olcontrol_OverviewMap
} from "ol/control";
import LayerSwitcher from "ol-layerswitcher/src/ol-layerswitcher.js";
import projdata from "../../public/data/output/thucnews/projection_dense_tfidf.json";
import similarityMatrix from "../../public/data/output/thucnews/similarity_matrix_5round.json";
import cluserdata from "../../public/data/output/thucnews/cluster.json";
import mapdata from "../../public/data/output/thucnews/mapdata.json";
import allDocKeywords from "../../public/data/output/thucnews/doc2keyword.json";
// { dataExtent, mapExtent, pointIndexInfo, polygons, finalPoints, ecoords, edge2docindex, paths, clusters }
export default {
  name: "FastMap",
  data() {
    return {
      map: null,
      layers: {
        colorLumpLayer: null,
        voronoiLayer: null,
        clusterLayer: null,
        roadLayer: null,
        wordLayer: null
      },
      wordSource: new olsource_Vector(),
      displayKeywords: null,
      firstForceSimulation: null,
      secondForceSimulation: null,
      zoom: 1,
      voronoiColor: null,
      shadeColor: null,
      roadwithScale: null
    };
  },
  created: function() {},
  beforeDestroy: function() {},
  mounted() {
    this.$nextTick(() => {
      let start = new Date();
      this.processData();
      this.initMap();
      this.addClickEventOnRoad();
      let end = new Date();
      console.log("耗时:", end - start);
    });
  },
  methods: {
    processData() {
      this.voronoiColor = d3
        .scaleSequential()
        .domain([0, 0.8])
        .interpolator(d3.interpolateYlGn); //interpolateBrBG,interpolateYlGn
      this.shadeColor = d3
        .scaleSequential()
        .domain([0, 20])
        .interpolator(d3.interpolateOranges); //interpolateBrBG,interpolateYlGn
      this.roadwithScale = d3
        .scaleLinear()
        .domain([0.2, 0.5])
        .range([1, 5]);

      console.log(mapdata);
    },
    initMap() {
      let instance = this;
      this.layers.colorLumpLayer = new ollayer_Vector({
        title: "ColorLump",
        source: this.addColorLump(),
        opacity: 0.5
      });
      this.layers.voronoiLayer = new ollayer_Vector({
        title: "Voronoi",
        source: this.addVoronoi()
        // opacity: 0.3
      });
      this.layers.clusterLayer = new ollayer_Vector({
        title: "Cluster",
        // type: "base",
        visible: false,
        source: this.addCluster(),
        opacity: 0.3
      });
      this.layers.roadLayer = new ollayer_Vector({
        title: "Road",
        source: this.addRoad()
      });
      this.layers.wordLayer = new ollayer_Vector({
        title: "Words",
        source: this.wordSource
      });
      this.map = new ol_Map({
        target: "fastmap",
        layers: [
          new ollayer_Group({
            title: "Base maps",
            layers: [
              new ollayer_Group({
                title: "Topography",
                // type: "base",
                combine: true,
                visible: true,
                layers: [
                  instance.layers.colorLumpLayer,
                  instance.layers.voronoiLayer
                ]
              }),
              instance.layers.clusterLayer
            ]
          }),
          new ollayer_Group({
            title: "Overlays",
            layers: [
              instance.layers.roadLayer,
              // new ollayer_Vector({
              //   title: "DocPoint",
              //   visible: false,
              //   source: this.addDocPoint()
              // }),
              instance.layers.wordLayer
            ]
          })
        ],
        controls: olcontrol_defaults().extend([
          // new olcontrol_OverviewMap({
          //   layers: [
          //     new ollayer_Group({
          //       layers: [
          //         new ollayer_Vector({
          //           source: this.addColorLump()
          //         }),
          //         new ollayer_Vector({
          //           source: this.addVoronoi()
          //         })
          //       ]
          //     })
          //   ]
          // }),
          new LayerSwitcher({
            tipLabel: "LayerSwitcher" // Optional label for button
          })
        ]),
        view: new ol_View({
          projection: new olproj_Projection({
            extent: mapdata.mapExtent
          }),
          extent: mapdata.mapExtent,
          center: olextent_getCenter(mapdata.mapExtent),
          zoom: 1
        })
      });
      this.map.on("moveend", function(e) {
        instance.zoom = instance.map.getView().getZoom(); //获取当前地图的缩放级别
        console.log("zoom: " + instance.zoom);
        let currentExtent = instance.map
          .getView()
          .calculateExtent(instance.map.getSize());
        instance.firstForceSimulation && instance.firstForceSimulation.stop();
        instance.secondForceSimulation && instance.secondForceSimulation.stop();
        let graphdata = instance.getWords(
          currentExtent,
          ~~(10 - instance.zoom * 2)
        );
        if (instance.zoom > 3) {
          instance.taglayout(graphdata, true);
        } else {
          instance.taglayout(graphdata);
        }
      });
      this.zoom = this.map.getView().getZoom();
      let graphdata = this.getOverviewWords(5);
      this.taglayout(graphdata);
      // this.addForce();
    },
    addDocPoint() {
      let vectorSource = new olsource_Vector();
      for (
        let i = mapdata.pointIndexInfo.dataPoint[0],
          len = mapdata.pointIndexInfo.dataPoint[1];
        i < len;
        i++
      ) {
        let feature = new ol_Feature({
          geometry: new olgeom_Point(mapdata.finalPoints[i])
        });
        feature.setStyle(
          new olstyle_Style({
            image: new olstyle_Circle({
              radius: 1,
              fill: new olstyle_Fill({ color: "black" })
            })
          })
        );
        vectorSource.addFeature(feature);
      }
      return vectorSource;
    },
    addBackground() {
      let vectorSource = new olsource_Vector();
      let background = new ol_Feature({
        geometry: new olgeom_Polygon([
          [
            [mapdata.mapExtent[0], mapdata.mapExtent[1]],
            [mapdata.mapExtent[2], mapdata.mapExtent[1]],
            [mapdata.mapExtent[2], mapdata.mapExtent[3]],
            [mapdata.mapExtent[0], mapdata.mapExtent[3]],
            [mapdata.mapExtent[0], mapdata.mapExtent[1]]
          ]
        ])
      });
      background.setStyle(
        new olstyle_Style({
          fill: new olstyle_Fill({
            color: "rgb(0, 191, 255)"
          })
        })
      );
      vectorSource.addFeature(background);
      return vectorSource;
    },
    addVoronoi() {
      let vectorSource = new olsource_Vector();
      mapdata.polygons.forEach((pg, index) => {
        let feature = new ol_Feature({
          geometry: new olgeom_Polygon([pg])
        });
        if (index >= mapdata.pointIndexInfo.dataPoint[1]) {
          //海洋或湖泊
          feature.setStyle(
            new olstyle_Style({
              fill: new olstyle_Fill({
                color: "rgb(0, 191, 255, 0.3)"
              })
            })
          );
        } else {
          feature.setStyle(
            new olstyle_Style({
              fill: new olstyle_Fill({
                color: "rgb(255, 255, 255, 0)"
              }),
              stroke: new olstyle_Stroke({
                color: "rgb(0, 0, 0, 0.2)"
              })
            })
          );
        }
        feature.setId("voronoi-" + index);
        vectorSource.addFeature(feature);
      });
      // mapdata.polygons.forEach((pg, index) => {
      //   if (index < mapdata.pointIndexInfo.dataPoint[1]) {
      //     let feature = new ol_Feature({
      //       geometry: new olgeom_Polygon([pg])
      //     });
      //     feature.setStyle(
      //       new olstyle_Style({
      //         fill: new olstyle_Fill({
      //           color: "rgb(255, 255, 255, 0)"
      //         }),
      //         stroke: new olstyle_Stroke({
      //           color: "rgb(0, 0, 0, 0.05)"
      //         })
      //       })
      //     );
      //     feature.setId("voronoi-" + index);
      //     vectorSource.addFeature(feature);
      //   }
      // });
      return vectorSource;
    },
    addCluster() {
      let clsuterNum = Object.keys(cluserdata).length;
      let color = d3
        .scaleSequential()
        .domain([0, clsuterNum])
        .interpolator(d3.interpolateYlGn);
      let vectorSource = new olsource_Vector();
      mapdata.polygons.forEach((pg, index) => {
        let feature = new ol_Feature({
          geometry: new olgeom_Polygon([pg])
        });
        if (index >= mapdata.pointIndexInfo.dataPoint[1]) {
          feature.setStyle(
            new olstyle_Style({
              fill: new olstyle_Fill({
                color: "rgb(0, 191, 255)"
              }),
              stroke: new olstyle_Stroke({
                color: "grey"
              })
            })
          );
        } else {
          feature.setStyle(
            new olstyle_Style({
              fill: new olstyle_Fill({
                color: color(mapdata.clusters[index])
              }),
              stroke: new olstyle_Stroke({
                color: "grey"
              })
            })
          );
        }
        feature.setId("clusterVoronoi-" + index);
        vectorSource.addFeature(feature);
      });
      return vectorSource;
    },
    addColorLump() {
      let vectorSource = new olsource_Vector();
      for (let edge in mapdata.edge2docindex) {
        let docindex = mapdata.edge2docindex[edge];
        docindex = docindex.map(d => +d);
        let pg = null;
        let weight = 0;
        let [p1, p2] = edge.split("-");
        p1 = parseInt(p1);
        p2 = parseInt(p2);
        if (docindex.length == 2) {
          if (
            docindex[0] < mapdata.pointIndexInfo.dataPoint[1] &&
            docindex[1] < mapdata.pointIndexInfo.dataPoint[1]
          ) {
            pg = [
              mapdata.ecoords[p1],
              mapdata.finalPoints[docindex[0]],
              mapdata.ecoords[p2],
              mapdata.finalPoints[docindex[1]],
              mapdata.ecoords[p1]
            ];
            weight = similarityMatrix[docindex[0]][docindex[1]];
          } else {
            // 有一个多边形表示海洋或湖泊
            if (
              docindex[0] < mapdata.pointIndexInfo.dataPoint[1] &&
              docindex[1] >= mapdata.pointIndexInfo.dataPoint[1]
            ) {
              pg = [
                mapdata.ecoords[p1],
                mapdata.finalPoints[docindex[0]],
                mapdata.ecoords[p2],
                mapdata.ecoords[p1]
              ];
              weight = 0;
            } else if (
              docindex[1] < mapdata.pointIndexInfo.dataPoint[1] &&
              docindex[0] >= mapdata.pointIndexInfo.dataPoint[1]
            ) {
              pg = [
                mapdata.ecoords[p1],
                mapdata.finalPoints[docindex[1]],
                mapdata.ecoords[p2],
                mapdata.ecoords[p1]
              ];
              weight = 0;
            }
          }
        } else if (docindex.length == 1) {
          if (docindex[0] < mapdata.pointIndexInfo.dataPoint[1]) {
            pg = [
              mapdata.ecoords[p1],
              mapdata.finalPoints[docindex[0]],
              mapdata.ecoords[p2],
              mapdata.ecoords[p1]
            ];
            weight = 0;
          }
        }
        if (pg == null) {
          continue;
        }
        let feature = new ol_Feature({
          geometry: new olgeom_Polygon([pg])
        });
        feature.setStyle(
          new olstyle_Style({
            fill: new olstyle_Fill({
              color: this.voronoiColor(weight)
            })
          })
        );
        vectorSource.addFeature(feature);
      }
      return vectorSource;
    },
    addRoad() {
      let vectorSource = new olsource_Vector();
      for (let pair in mapdata.paths) {
        let path = mapdata.paths[pair];
        let pairArr = pair.split("-");
        let feature = new ol_Feature({
          geometry: new olgeom_LineString(path)
        });
        feature.setStyle(
          new olstyle_Style({
            stroke: new olstyle_Stroke({
              color: "rgb(255, 165, 0, 0.3)",
              width: this.roadwithScale(
                similarityMatrix[+pairArr[0]][+pairArr[1]]
              )
            })
          })
        );
        vectorSource.addFeature(feature);
      }
      return vectorSource;
    },
    addForce() {
      // let word2doclist = {};
      // Object.keys(cluserdata).forEach(category => {
      //   cluserdata[category].forEach(docid => {
      //     let kws = allDocKeywords[docid.toString()];
      //     kws.forEach(word => {
      //       let key = category + "-" + word;
      //       if (word2doclist[key] === undefined) {
      //         word2doclist[key] = [docid];
      //       } else {
      //         word2doclist[key].push(docid);
      //       }
      //     });
      //   });
      // });
      // let wordArray = Object.keys(word2doclist).filter(
      //   d => word2doclist[d].length > 5
      // );
      // let domain = mapdata.pointIndexInfo.dataPoint;
      // let nodes = [];
      // let links = [];
      // for (let i = domain[0]; i < domain[1]; i++) {
      //   nodes.push({
      //     id: i,
      //     category: "point",
      //     x: mapdata.finalPoints[i][0],
      //     y: mapdata.finalPoints[i][1]
      //   });
      // }
      // for (let i = 0, len = wordArray.length; i < len; i++) {
      //   nodes.push({
      //     id: domain[1] + i,
      //     category: "tag",
      //     word: wordArray[i].split("-")[1]
      //   });
      //   word2doclist[wordArray[i]].forEach(docid => {
      //     links.push({
      //       source: docid,
      //       target: domain[1] + i
      //     });
      //   });
      // }
      // let graph = { nodes: nodes, links: links };

      let domain = mapdata.pointIndexInfo.dataPoint;
      let nodes = [];
      let links = [];
      for (let i = domain[0]; i < domain[1]; i++) {
        nodes.push({
          id: i,
          category: "point",
          x: mapdata.finalPoints[i][0],
          y: mapdata.finalPoints[i][1]
        });
      }
      let count = domain[1];
      Object.keys(allDocKeywords).forEach(key => {
        for (let i = 0; i < 5; i++) {
          nodes.push({
            id: count,
            category: "tag",
            word: allDocKeywords[key][i]
          });
          links.push({
            source: +key,
            target: count
          });
          count++;
        }
      });
      let graph = { nodes: nodes, links: links };

      let instance = this;
      let nodesCopy = _.cloneDeep(graph.nodes);
      let fixedNodes = graph.nodes.filter(d => d.category === "point");

      let force = d3
        .forceSimulation(graph.nodes)
        .force("charge", d3.forceManyBody().distanceMax(0.02))
        .force(
          "link",
          d3
            .forceLink(graph.links)
            .distance(0.5)
            .id(d => d.id)
        )
        .alphaMin(0.02)
        .on("tick", tick);

      let link = d3
        .selectAll(".link")
        .data(graph.links)
        .enter();

      let node = d3
        .selectAll(".node")
        .data(graph.nodes)
        .enter();

      function tick() {
        console.log("tick1");
        fixedNodes = fixedNodes.map(d =>
          Object.assign(d, { fx: nodesCopy[d.id].x, fy: nodesCopy[d.id].y })
        );
      }

      force.on("end", function() {
        console.log("end...");
        let vectorSource = new olsource_Vector();
        node.each(function(d, i) {
          if (d.category === "tag") {
            let feature = new ol_Feature({
              geometry: new olgeom_Point([d.x, d.y])
            });
            feature.setStyle(
              new olstyle_Style({
                text: new olstyle_Text({
                  font: "10px Microsoft YaHei",
                  text: d.word,
                  fill: new olstyle_Fill({
                    color: "#222"
                  })
                })
              })
            );
            vectorSource.addFeature(feature);
          }
        });
        link.each(function(d) {
          let feature = new ol_Feature({
            geometry: new olgeom_LineString([
              [d.source.x, d.source.y],
              [d.target.x, d.target.y]
            ])
          });
          feature.setStyle(
            new olstyle_Style({
              stroke: new olstyle_Stroke({
                color: "rgb(255, 0, 0, 0.1)"
              })
            })
          );
          vectorSource.addFeature(feature);
        });
        let layer = new ollayer_Vector({
          title: "Force",
          source: vectorSource
        });
        instance.map.addLayer(layer);
      });
    },
    getOverviewWords(n) {
      let word2doclist = {};
      Object.keys(cluserdata).forEach(category => {
        cluserdata[category].forEach(docid => {
          let kws = allDocKeywords[docid.toString()];
          kws.forEach(word => {
            let key = category + "-" + word;
            if (word2doclist[key] === undefined) {
              word2doclist[key] = [docid];
            } else {
              word2doclist[key].push(docid);
            }
          });
        });
      });
      let wordArray = [];
      Object.keys(word2doclist).forEach(d => {
        if (word2doclist[d].length > n) {
          wordArray.push({
            cluster: d.split("-")[0],
            word: d.split("-")[1],
            doclist: word2doclist[d]
          });
        }
      });
      this.displayKeywords = wordArray;

      let domain = mapdata.pointIndexInfo.dataPoint;
      let nodes = [];
      let links = [];
      for (let i = domain[0]; i < domain[1]; i++) {
        nodes.push({
          id: i,
          category: "point",
          x: mapdata.finalPoints[i][0],
          y: mapdata.finalPoints[i][1]
        });
      }
      for (let i = 0, len = wordArray.length; i < len; i++) {
        nodes.push({
          id: domain[1] + i,
          category: "tag",
          cluster: wordArray[i].cluster,
          word: wordArray[i].word,
          doclist: wordArray[i].doclist
        });
        wordArray[i].doclist.forEach(docid => {
          links.push({
            source: docid,
            target: domain[1] + i
          });
        });
      }

      console.log(
        "word number: ",
        nodes.filter(d => d.category === "tag").length
      );
      let graph = { nodes: nodes, links: links };
      return graph;
    },
    getWords(extent, n) {
      let word2doclist = {};
      Object.keys(cluserdata).forEach(category => {
        cluserdata[category].forEach(docid => {
          if (
            mapdata.finalPoints[docid][0] > extent[0] &&
            mapdata.finalPoints[docid][0] < extent[2] &&
            mapdata.finalPoints[docid][1] > extent[1] &&
            mapdata.finalPoints[docid][1] < extent[3]
          ) {
            let kws = allDocKeywords[docid.toString()];
            kws.forEach(word => {
              let key = category + "-" + word;
              if (word2doclist[key] === undefined) {
                word2doclist[key] = [docid];
              } else {
                word2doclist[key].push(docid);
              }
            });
          }
        });
      });
      let wordArray = [];
      Object.keys(word2doclist).forEach(d => {
        if (word2doclist[d].length > n) {
          wordArray.push({
            cluster: d.split("-")[0],
            word: d.split("-")[1],
            doclist: word2doclist[d]
          });
        }
      });
      this.displayKeywords = wordArray;

      let domain = mapdata.pointIndexInfo.dataPoint;
      let nodes = [];
      let links = [];
      for (let i = domain[0]; i < domain[1]; i++) {
        nodes.push({
          id: i,
          category: "point",
          x: mapdata.finalPoints[i][0],
          y: mapdata.finalPoints[i][1]
        });
      }
      for (let i = 0, len = wordArray.length; i < len; i++) {
        nodes.push({
          id: domain[1] + i,
          category: "tag",
          cluster: wordArray[i].cluster,
          word: wordArray[i].word,
          doclist: wordArray[i].doclist
        });
        wordArray[i].doclist.forEach(docid => {
          links.push({
            source: docid,
            target: domain[1] + i
          });
        });
      }

      console.log(
        "word number: ",
        nodes.filter(d => d.category === "tag").length
      );
      let graph = { nodes: nodes, links: links };
      return graph;
    },
    getWidthOfText(txt, fontname, fontsize) {
      let canvas = document.createElement("canvas");
      let ctx = canvas.getContext("2d");
      ctx.font = fontsize + " " + fontname;
      return ctx.measureText(txt).width;
    },
    taglayout(graph, diffFontsize = false) {
      let instance = this;
      let nodesCopy = _.cloneDeep(graph.nodes);
      let fixedNodes = graph.nodes.filter(d => d.category === "point");

      instance.firstForceSimulation = d3
        .forceSimulation(graph.nodes)
        .force("charge", d3.forceManyBody().distanceMax(0.02))
        .force(
          "link",
          d3
            .forceLink(graph.links)
            .distance(0.5)
            .id(d => d.id)
        )
        .alphaMin(0.02)
        .on("tick", tick);

      // let link = d3
      //   .selectAll(".link")
      //   .data(graph.links)
      //   .enter();

      // let node = d3
      //   .selectAll(".node")
      //   .data(graph.nodes)
      //   .enter();

      function tick() {
        console.log("tick1");
        fixedNodes = fixedNodes.map(d =>
          Object.assign(d, { fx: nodesCopy[d.id].x, fy: nodesCopy[d.id].y })
        );
      }

      instance.firstForceSimulation.on("end", function() {
        console.log("end...");
        const fontname = "Microsoft YaHei";
        const fontsize = "10px";
        let tagNodes = graph.nodes.filter(d => d.category === "tag");

        for (let i = 0; i < tagNodes.length; i++) {
          let newfontsize = ~~fontsize.split("px")[0];
          if (diffFontsize) {
            newfontsize =
              newfontsize +
              Math.log(tagNodes[i].doclist.length) * instance.zoom;
          }
          newfontsize = ~~newfontsize;
          let pixelWidth = instance.getWidthOfText(
            tagNodes[i].word,
            fontname,
            newfontsize + "px"
          );
          let extent = instance.map
            .getView()
            .calculateExtent([pixelWidth, newfontsize]);
          tagNodes[i].width = extent[2] - extent[0];
          tagNodes[i].height = extent[3] - extent[1];
          tagNodes[i].fontsize = newfontsize;
        }

        // let tagnode = d3
        //   .selectAll(".tagnode")
        //   .data(tagNodes)
        //   .enter();

        // let center = instance.map.getView().getCenter();
        instance.secondForceSimulation = d3
          .forceSimulation(tagNodes)
          .force("charge", d3.forceManyBody().strength(0))
          // .force('center', d3.forceCenter(center[0], center[1]))
          .alphaMin(0.2)
          .on("tick", function() {
            console.log("tick2");
            let q = d3
                .quadtree()
                .x(d => d.x)
                .y(d => d.y)
                .addAll(tagNodes),
              i = 0,
              n = tagNodes.length;
            while (++i < n) {
              q.visit(collide(tagNodes[i]));
            }
          });

        function collide(node) {
          return function(quad, x1, y1, x2, y2) {
            var updated = false;
            if (quad.data && quad.data !== node) {
              var x = node.x - quad.data.x,
                y = node.y - quad.data.y,
                xSpacing = (quad.data.width + node.width) / 2,
                ySpacing = (quad.data.height + node.height) / 2,
                absX = Math.abs(x),
                absY = Math.abs(y),
                l,
                lx,
                ly;

              if (absX < xSpacing && absY < ySpacing) {
                l = Math.sqrt(x * x + y * y);

                lx = (absX - xSpacing) / l;
                ly = (absY - ySpacing) / l;

                // the one that's barely within the bounds probably triggered the collision
                if (Math.abs(lx) > Math.abs(ly)) {
                  lx = 0;
                } else {
                  ly = 0;
                }

                node.x -= x *= lx;
                node.y -= y *= ly;
                quad.data.x += x;
                quad.data.y += y;

                updated = true;
              }
            }
            return updated;
          };
        }

        instance.secondForceSimulation.on("end", function() {
          if (instance.wordSource.getFeatures().length > 0) {
            instance.wordSource.clear();
          }
          tagNodes.forEach(function(d, i) {
            if (d.category === "tag") {
              let textFeature = new ol_Feature({
                geometry: new olgeom_Point([d.x, d.y])
              });
              textFeature.setStyle(
                new olstyle_Style({
                  text: new olstyle_Text({
                    font: d.fontsize + "px " + fontname,
                    text: d.word,
                    fill: new olstyle_Fill({
                      color: "#222"
                    })
                  })
                })
              );
              textFeature.setId("text-" + i);
              let shadeFeature = new ol_Feature({
                geometry: new olgeom_Polygon([
                  [
                    [d.x - d.width / 2, d.y - d.height / 2],
                    [d.x + d.width / 2, d.y - d.height / 2],
                    [d.x + d.width / 2, d.y + d.height / 2],
                    [d.x - d.width / 2, d.y + d.height / 2],
                    [d.x - d.width / 2, d.y - d.height / 2]
                  ]
                ])
              });
              shadeFeature.setStyle(
                new olstyle_Style({
                  fill: new olstyle_Fill({
                    color: instance
                      .shadeColor(d.doclist.length)
                      .replace(")", ", 0.5)") //"rgb(255, 255, 255, 0.8)"
                  })
                })
              );
              shadeFeature.setId("shade-" + i);
              instance.wordSource.addFeature(textFeature);
              instance.wordSource.addFeature(shadeFeature);
            }
          });
        });
      });
    },
    addClickEventOnRoad() {
      let selectSingleClick = new olinteraction_Select();
      let instance = this;
      selectSingleClick.on("select", function(e) {
        // console.log(e);
        e.selected.forEach(feature => {
          let featureId = feature.getId();
          let featureType = featureId.split("-")[0];
          let featureIndex = featureId.split("-")[1];
          switch (featureType) {
            case "text":
            case "shade":
              (function() {
                let obj = instance.displayKeywords[+featureIndex];
                let features = instance.layers.voronoiLayer
                  .getSource()
                  .getFeatures();
                for (let i in features) {
                  let index = ~~features[i].getId().split("-")[1];
                  if (
                    index >= mapdata.pointIndexInfo.dataPoint[0] &&
                    index < mapdata.pointIndexInfo.dataPoint[1]
                  ) {
                    if (obj.doclist.includes(index)) {
                      features[i].setStyle(
                        new olstyle_Style({
                          fill: new olstyle_Fill({
                            color: "rgb(255, 0, 0, 0.3)"
                          }),
                          stroke: new olstyle_Stroke({
                            color: "rgb(0, 0, 0, 0.2)"
                          })
                        })
                      );
                    } else {
                      features[i].setStyle(
                        new olstyle_Style({
                          fill: new olstyle_Fill({
                            color: "rgb(255, 255, 255, 0)"
                          }),
                          stroke: new olstyle_Stroke({
                            color: "rgb(0, 0, 0, 0.2)"
                          })
                        })
                      );
                    }
                  }
                }
              })();
              break;
            default:
              break;
          }
        });
        e.deselected.forEach(feature => {});
      });
      this.map.addInteraction(selectSingleClick);
    }
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang='scss' scoped>
.fastmap-container {
  width: 100%;
  height: 100%;

  #fastmap {
    width: 100%;
    height: 100%;

    /deep/ .layer-switcher {
      ul {
        padding-left: 1em;
      }
    }
  }
}
</style>
