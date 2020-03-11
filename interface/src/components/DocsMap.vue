<template>
  <div class="docsmap-container">
    <div id="docsmap"></div>
  </div>
</template>
<script>
import * as api from "../assets/js/http.js";
import {
  getExtent,
  getVoronoi,
  genRandomPoints
} from "../assets/js/processMap";
import * as d3 from "d3";
import { Map as ol_Map, View as ol_View, Feature as ol_Feature } from "ol";
import {
  Tile as ollayer_Tile,
  Group as ollayer_Group,
  Vector as ollayer_Vector,
  Image as ollayer_Image
} from "ol/layer";
import {
  OSM as olsource_OSM,
  Vector as olsource_Vector,
  ImageCanvas as olsource_ImageCanvas
} from "ol/source";
import { Projection as olproj_Projection } from "ol/proj";
import { getCenter as olextent_getCenter } from "ol/extent";
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
export default {
  name: "DocsMap",
  data() {
    return {
      map: null,
      layers: {
        docpointLayer: null,
        voronoiLayer: null,
        canvasLayer: null,
        gridlineLayer: null,
      },
      mapConfig: {
        extent: null
      },
      data: {
        projList: null
      }
    };
  },
  async mounted() {
    let proj = await api.getProj();
    this.data.projList = proj.data.datum;
    this.preProcess();
    this.initMap();
    this.addLayers();
  },
  methods: {
    preProcess() {
      this.mapConfig.extent = getExtent(this.data.projList);
      console.log(this.mapConfig.extent);
    },
    initMap() {
      let instance = this;
      this.map = new ol_Map({
        target: "docsmap",
        layers: [
          // new ollayer_Tile({
          //   source: new olsource_OSM()
          // })
        ],
        view: new ol_View({
          // extent: this.mapConfig.extent,
          projection: new olproj_Projection({
            extent: this.mapConfig.extent
          }),
          center: olextent_getCenter(this.mapConfig.extent),
          zoom: 2.5
        })
      });
    },
    addLayers() {
      const cellWidth = Math.floor(
        (this.mapConfig.extent[2] - this.mapConfig.extent[0]) / 50
      );
      // let randomPoints = genRandomPoints(
      //   this.data.projList,
      //   this.mapConfig.extent,
      //   cellWidth,
      //   5
      // );
      // let allPoints = this.data.projList.concat(randomPoints);
      // let polygons = getVoronoi(this.mapConfig.extent, allPoints, 50);
      // allPoints = null; // 释放内存

      // this.layers.voronoiLayer = this.addVoronoiLayer(polygons);
      // this.map.addLayer(this.layers.voronoiLayer);

      // allPoints = polygons.map(pg => d3.polygonCentroid(pg));
      this.layers.docpointLayer = this.addPointLayer(this.data.projList);
      this.map.addLayer(this.layers.docpointLayer);
      // this.layers.canvasLayer = this.addCanvasLayer();
      // this.map.addLayer(this.layers.canvasLayer);
      this.layers.gridlineLayer = this.addGridlineLayer();
      this.map.addLayer(this.layers.gridlineLayer);
    },
    addPointLayer(points) {
      let vectorSource = new olsource_Vector();
      let layer = new ollayer_Vector({
        source: vectorSource
      });
      let length = this.data.projList.length;
      for (let i = 0, len = length; i < len; i++) {
        let feature = new ol_Feature({
          geometry: new olgeom_Point(points[i])
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
      return layer;
    },
    addVoronoiLayer(polygons) {
      let vectorSource = new olsource_Vector();
      let layer = new ollayer_Vector({
        source: vectorSource
      });
      polygons.forEach((pg, index) => {
        let feature = new ol_Feature({
          geometry: new olgeom_Polygon([pg])
        });
        feature.setStyle(
          new olstyle_Style({
            // fill: new olstyle_Fill({
            //   color: "rgb(0, 191, 255, 0.3)"
            // }),
            stroke: new olstyle_Stroke({
              color: "rgb(0, 0, 0, 0.05)"
            })
          })
        );
        feature.setId("voronoi-" + index);
        vectorSource.addFeature(feature);
      });
      return layer;
    },
    addCanvasLayer() {
      let instance = this;
      let isFirst = true;
      let layer = new ollayer_Image({
        source: new olsource_ImageCanvas({
          canvasFunction: function(
            extent,
            resolution,
            pixelRatio,
            size,
            projection
          ) {
            if (isFirst) {
              isFirst = false;
              let [width, height] = size; //画布尺寸
              let [left, bottom, right, top] = extent; //坐标投影
              let xScale = width / (right - left); //画布尺寸与坐标投影比
              let yScale = height / (top - bottom);
              let canvas = document.createElement("canvas");
              canvas.width = size[0];
              canvas.height = size[1];
              canvas.style.display = "block";
              let ctx = canvas.getContext("2d");
              ctx.clearRect(0, 0, canvas.width, canvas.height);
              ctx.fillStyle = "rgb(255, 0, 0, 0.2)";
              ctx.fillRect(0, 0, canvas.width, canvas.height);
              return canvas;
            }
          }
        })
      });
      return layer;
    },
    addGridlineLayer() {
      const cellWidth = (this.mapConfig.extent[2] - this.mapConfig.extent[0]) / 50;
      let innerXNum = Math.ceil((this.mapConfig.extent[2] - this.mapConfig.extent[0]) / cellWidth);
      let innerYNum = Math.ceil((this.mapConfig.extent[3] - this.mapConfig.extent[1]) / cellWidth);
      let xScale = d3
        .scaleQuantize()
        .domain([this.mapConfig.extent[0], this.mapConfig.extent[2]])
        .range(d3.range(0, innerXNum));
      let yScale = d3
        .scaleQuantize()
        .domain([this.mapConfig.extent[1], this.mapConfig.extent[3]])
        .range(d3.range(0, innerYNum));

      let source = new olsource_Vector();
      let layer = new ollayer_Vector({
        source: source
      });

      for (let i = 0; i < innerXNum; i++) {
        // 画竖线
        let feature = new ol_Feature({
          geometry: new olgeom_LineString([
            [this.mapConfig.extent[0] + i * cellWidth, this.mapConfig.extent[1]],
            [this.mapConfig.extent[0] + i * cellWidth, this.mapConfig.extent[3]]
          ])
        });
        feature.setStyle(
          new olstyle_Style({
            stroke: new olstyle_Stroke({
              color: "rgb(255, 165, 0, 0.3)",
            })
          })
        );
        source.addFeature(feature);
      }
      for (let i = 0; i < innerYNum; i++) {
        // 画横线
        let feature = new ol_Feature({
          geometry: new olgeom_LineString([
            [this.mapConfig.extent[0], this.mapConfig.extent[1] + i * cellWidth],
            [this.mapConfig.extent[2], this.mapConfig.extent[1] + i * cellWidth]
          ])
        });
        feature.setStyle(
          new olstyle_Style({
            stroke: new olstyle_Stroke({
              color: "rgb(255, 165, 0, 0.3)",
            })
          })
        );
        source.addFeature(feature);
      }
      return layer;
    }
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang='scss' scoped>
.docsmap-container {
  width: 100%;
  height: 100%;

  #docsmap {
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