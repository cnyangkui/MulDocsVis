<template>
  <div class="radial-container">
    <div id="chart"></div>
    <div id="control">
      <!-- <div class="slider-block">
        <span class="demonstration">过滤</span>
        <el-slider v-model="docNum" :max="10" show-input></el-slider>
      </div>-->
      <div class="wordlist">
        <div v-for="item of processedData.keywords" :key="item.key">
          <div v-html="item.html"></div>
          <el-divider></el-divider>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import * as d3 from "d3";
import { getRequest } from "../assets/js/api.js";
export default {
  name: "RadialLayout",
  data() {
    return {
      requestData: {
        optimizedTree: null
      },
      processedData: {
        selectedSubTree: null,
        keywords: null
      },
      docNum: 5,
      wordlist: []
    };
  },
  mounted() {
    let instance = this;
    getRequest("/optimizedTree", {}, function(res) {
      console.log(res.data);
      instance.renderChart(res.data);
    });
  },
  methods: {
    renderChart(data) {
      let instance = this;
      instance.requestData.optimizedTree = data;
      // var data = [1, 1, 2, 3, 5, 8, 13];
      data = data.children;
      for (let i = 0; i < data.length; i++) {
        data[i].leaf = instance.getLeafNodes(data[i]);
        data[i].size = data[i].leaf.length;
      }
      data = data.filter(d => d.size > 5);
      instance.processedData.selectedSubTree = data;
      console.log(instance.requestData.optimizedTree);
      console.log(instance.processedData.selectedSubTree);

      let screenWidth = document.body.clientWidth;
      let screenHeight = document.body.clientHeight;
      let width = screenWidth * 0.7,
        height = screenHeight;

      let svg = d3
        .select("#chart")
        .append("svg")
        .attr("width", width)
        .attr("height", height);
      let g_all = svg.append("g");
      let g_arc = g_all.append("g").attr("class", "arc");

      let radius = Math.min(width, height) / 2 - 30;

      var colors = [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf"
      ];

      let pie = d3
        .pie()
        .padAngle(0.01)
        .value(d => d.size);

      console.log(d3.sum(data, d => d.size));

      let arc = d3
        .arc()
        .innerRadius(radius - 10)
        .outerRadius(radius);

      var arcs = pie(data);

      g_arc
        .selectAll("path")
        .data(arcs)
        .join("path")
        .attr("fill", "steelblue")
        .attr("d", arc)
        .attr("transform", `translate(${width / 2},${height / 2})`);

      instance.processedData.keywords = [];
      data.forEach((element, index) => {
        let ids = instance.getLeafNodes(element);
        getRequest(
          "/keywords/",
          {
            type: "doc2keywords",
            ids: ids,
            topK: 5
          },
          function(res) {
            let word2count = new Map();
            res.data.keywords.forEach(keywords => {
              keywords.words.forEach(word => {
                if (word2count.has(word)) {
                  word2count.set(word, word2count.get(word) + 1);
                } else {
                  word2count.set(word, 1);
                }
              });
            });
            let objArr = Array.from(word2count);
            objArr.sort((a, b) => b[1] - a[1]);
            let html = "";
            objArr.forEach(value => {
              let fontSize = 6 + Math.sqrt(value[1]) * 5;
              html += `<span style="font-size:${fontSize}pt">${value[0]}</span>&nbsp;`;
            });
            instance.processedData.keywords.push({
              key: element.name,
              value: res.data.keywords,
              set: objArr,
              html: html
            });
          }
        );
      });
    },
    getWords(ids) {
      let instance = this;
      instance.wordlist = [];
    },
    getLeafNodes(root) {
      let queue = [],
        ids = [];
      queue.push(root);
      while (queue.length > 0) {
        let first = queue.shift();
        if (first.children != undefined) {
          for (let i = 0; i < first.children.length; i++) {
            queue.push(first.children[i]);
          }
        } else {
          ids.push(first.name);
        }
      }
      return ids;
    }
  }
};
</script>
<style lang="scss" scoped>
// * {
//   border: 1px solid red;
// }
.radial-container {
  width: 100%;
  height: 100%;

  #chart {
    width: 70%;
    height: 100%;
    float: left;
    border: 1px solid grey;

    /deep/ .link {
      fill: none;
      stroke: gray;
    }
  }
  #control {
    width: 30%;
    height: 100%;
    float: left;
    border: 1px solid grey;

    .slider-block {
      width: 80%;
      margin: 0 auto;
    }

    .wordlist {
      height: 100%;
      overflow-y: auto;
      border: 1px solid grey;

      input,
      .p-word {
        margin-bottom: 3px;
      }
    }
  }
}
</style>