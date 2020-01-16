<template>
  <div class="docsmap-container">
    <div id="docsmap"></div>
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
import { getProj } from "../assets/js/http.js";
import {
  getExtent,
  generateOuterPoints,
  generateInnerPoints,
  getVoronoi
} from "../assets/js/processMapData.js";
export default {
  name: "DocsMap",
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
      data: {
        mapExtent: null,
        allPoints: null,
        pointIndexInfo: null
      },
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
  async mounted() {
    let start = new Date();
    const response = await getProj();
    this.processData(response.data.projlist);
    this.initMap();
    let end = new Date();
    console.log("耗时:", end - start);
  },
  methods: {
    processData(projdata) {
      const { dataExtent, mapExtent } = getExtent(projdata);
      let outerPoints = generateOuterPoints(dataExtent, mapExtent, 200);
      let innerPoints = generateInnerPoints(projdata, dataExtent, 20, 20);
      this.data.allPoints = projdata;
      //   .concat(outerPoints).concat(innerPoints);
      // this.data.pointIndexInfo = {
      //   dataPoint: [0, projdata.length],
      //   outerPoint: [projdata.length, projdata.length + outerPoints.length],
      //   innerPoint: [
      //     projdata.length + outerPoints.length,
      //     this.data.allPoints.length
      //   ]
      // };
      this.data.mapExtent = mapExtent;
    },
    initMap() {
      let instance = this;
      this.map = new ol_Map({
        target: "docsmap",
        view: new ol_View({
          projection: new olproj_Projection({
            extent: instance.data.mapExtent
          }),
          extent: instance.data.mapExtent,
          center: olextent_getCenter(instance.data.mapExtent),
          zoom: 1
        })
      });
      this.addVoronoi();
    },
    addVoronoi() {
      let polygons = d3
        .voronoi()
        .extent([
          [this.data.mapExtent[0], this.data.mapExtent[1]],
          [this.data.mapExtent[2], this.data.mapExtent[3]]
        ])
        .polygons(this.data.allPoints);

      // let polygons = getVoronoi(this.data.mapExtent, this.data.allPoints, 100);
      let vectorSource = new olsource_Vector();
      this.layers.voronoiLayer = new ollayer_Vector({
        source: vectorSource
      });
      for (let i in polygons) {
        let pg = polygons[i];
        pg.push(pg[0]);
        let feature = new ol_Feature({
          geometry: new olgeom_Polygon([pg])
        });
        feature.setStyle(
          new olstyle_Style({
            // fill: new olstyle_Fill({
            //   color: "rgb(0, 191, 255)"
            // }),
            stroke: new olstyle_Stroke({
              color: "grey"
            })
          })
        );
        feature.setId("voronoi-" + i);
        vectorSource.addFeature(feature);
      }
      this.map.addLayer(this.layers.voronoiLayer);
    },
    addCluster() {},
    addColorLump() {}
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang='scss' scoped>
.docsmap-container {
  width: 100%;
  height: 100%;

  #docsmap {
    width: 60%;
    height: 90%;

    /deep/ .layer-switcher {
      ul {
        padding-left: 1em;
      }
    }
  }
}
</style>
