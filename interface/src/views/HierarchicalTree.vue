<template>
  <div class="tree-container">
    <div id="tree"></div>
    <div id="control">
      <div>
        文档ID：<input type="text" v-model="docid"/>
        <input type="button" value="确定" @click="search" />
      </div>
      <div>
        <input type="radio" value="keywords" v-model="wordtype" />关键词
        <input type="radio" value="commonwords" v-model="wordtype" />普通词
      </div>
      <div> 关键词 topK：<input type="text" v-model="topK" /></div>
      <div class="wordlist">
        <p class="p-word">查询文档：{{ids}}</p>
        <p v-for="item of wordlist" :key="item.key" class="p-word">{{item.value}}</p>
      </div>
    </div>
  </div>
</template>
<script>
import * as d3 from "d3";
import { getRequest } from "../assets/js/api.js";
// import treedata from "../assets/data/tree.json";
export default {
  name: "HierarchicalTree",
  data() {
    return {
      docid: null,
      wordtype: "keywords",
      wordlist: [],
      ids: [],
      topK: 20,
    };
  },
  mounted() {
    let that = this;
    getRequest("/htree", {}, function(res) {
      // console.log(res.data)
      that.renderTree(res.data);
    });
  },
  methods: {
    renderTree(treedata) {
      let that = this;
      let screenWidth = document.body.clientWidth;
      let screenHeight = document.body.clientHeight;
      let width = screenWidth * 0.7,
        height = screenHeight;
      let svg = d3
        .select("#tree")
        .append("svg")
        .attr("width", width)
        .attr("height", height);
      let g = svg.append("g");
      let cluster = d3.cluster().size([2 * Math.PI, height / 2 - 50]);
      svg.call(d3.zoom().on("zoom", zoomed));
      // svg
      //   .append("rect")
      //   .attr("width", width)
      //   .attr("height", height)
      //   .style("fill", "none")
      //   .style("pointer-events", "all")
      //   .call(
      //     d3
      //       .zoom()
      //       // .scaleExtent([1 / 2, 4])
      //       .on("zoom", zoomed)
      //   );

      function zoomed() {
        g.attr("transform", d3.event.transform);
      }

      var hierarchy = d3.hierarchy(treedata);
      cluster(hierarchy);
      var descendants = hierarchy.descendants();
      // console.log(descendants)
      // fontSize.domain(
      //   d3.extent(descendants, function(d) {
      //     return d.depth;
      //   })
      // );

      var link = g
        .selectAll(".link")
        .data(descendants.slice(1))
        .enter()
        .append("path")
        .attr("class", "link")
        .attr("d", function(d) {
          if (d.parent === descendants[0]) {
            return (
              "M" + project(d.x, d.y) + " " + project(d.parent.x, d.parent.y)
            );
          } else {
            return (
              "M" +
              project(d.x, d.y) +
              "C" +
              project(d.x, (d.y + d.parent.y) / 2) +
              " " +
              project(d.parent.x, (d.y + d.parent.y) / 2) +
              " " +
              project(d.parent.x, d.parent.y)
            );
          }
        });

      var node = g
        .selectAll(".node")
        .data(descendants)
        .enter()
        .append("g")
        .attr("transform", function(d) {
          return "translate(" + project(d.x, d.y) + ")";
        });

      node
        .filter(x => x.children == undefined)
        .append("text")
        .text(function(d) {
          return d.data.name;
        })
        .attr("font-size", function(d) {
          return "2px"; //fontSize(d.depth) + "pt";
        })
        .attr("transform", function(d) {
          var theta = (-d.x / Math.PI) * 180 + 90;
          if (d.x > Math.PI) {
            theta += 180;
          }
          if (d.depth !== 3 && Math.abs(theta) < 30) {
            theta = 0;
          }
          if (d.depth > 1) {
            return "rotate(" + theta + ")";
          } else {
            return "";
          }
        })
        .attr("text-anchor", function(d) {
          if (d.depth === 3) {
            return d.x > Math.PI ? "end" : "start";
          } else {
            return "middle";
          }
        })
        .attr("dx", function(d) {
          if (d.depth === 3) {
            return d.x > Math.PI ? "-2px" : "2px";
          } else {
            return "0px";
          }
        })
        .classed("glow", function(d) {
          return d.depth !== 3;
        })
        .attr("alignment-baseline", "central");

      node
        .append("circle")
        .attr("r", 2)
        .attr("fill", "steelblue")
        .attr("opacity", 0.3)
        .on("click", function(d, i) {
          that.docid = d.data.name;
          that.ids = that.preOrder(d);
          console.log(that.ids);
          that.search();
          that.getWords();
        });

      function project(theta, r) {
        return [
          width / 2 + r * Math.sin(theta),
          height / 2 + r * Math.cos(theta) + 4
        ];
      }
    },
    search() {
      let docid = parseInt(this.docid);
      d3.select("svg")
        .selectAll("circle")
        .attr("fill", function(d) {
          if (d.data.name == docid) {
            console.log(d.data);
            return "red";
          } else {
            return "steelblue";
          }
        })
        .attr("r", function(d) {
          if (d.data.name == docid) {
            return 8;
          } else {
            return 2;
          }
        });
    },
    getWords() {
      let that = this;
      that.wordlist = [];
      if (that.wordtype === "keywords") {
        getRequest(
          "/keywords/",
          {
            ids: that.ids,
            topK: parseInt(that.topK)
          },
          function(res) {
            that.wordlist = res.data.keywords.map((d, i) => {
              return { key: i, value: d };
            });
            console.log(that.wordlist);
          }
        );
      } else if (that.wordtype === "commonwords") {
        getRequest(
          "/commonwords/",
          {
            ids: that.ids,
            topK: parseInt(that.topK)
          },
          function(res) {
            that.wordlist = res.data.commonWords.map((d, i) => {
              return { key: i, value: d };
            });
            console.log(that.wordlist);
          }
        );
      }
    },
    preOrder(root) {
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
          ids.push(first.data.name);
        }
      }
      return ids;
    }
  },
  watch: {
    wordtype(n, o) {
      this.getWords()
    },
    topK(n, o) {
      this.getWords();
    }
  },
};
</script>
<style lang="scss" scoped>
// * {
//   border: 1px solid red;
// }
.tree-container {
  width: 100%;
  height: 100%;

  #tree {
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