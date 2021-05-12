<template>
  <div class="radial-container">
    <div id="chart"></div>
    <div id="control">
      <!-- <div class="slider-block">
        <span class="demonstration">过滤</span>
        <el-slider v-model="docNum" :max="10" show-input></el-slider>
      </div>-->
      <div class="wordlist">
        <div v-if="topics != null">
          <div v-for="item of topics" :key="item.key">
            <div v-html="item.html"></div>
            <el-divider></el-divider>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import * as d3 from "d3";
import * as _ from "lodash";
import { getRequest } from "../assets/js/api.js";
export default {
  name: "RadialLayout",
  data() {
    return {
      requestOptimizedTree: null,
      requestDoc2keywords: null,
      doc2keywordsMap: null,
      selectedSubTree: null,
      topics: null,
      nodes: null,
      links: null,
      subtreeNodes2root: null,
      docNum: 5,
      chart: {
        width: null,
        height: null,
        radius: null,
        arcs: null
      }
    };
  },
  mounted() {
    let instance = this;
    getRequest("/optimizedTree", {}, function(res) {
      instance.renderChart(res.data);
    });
  },
  methods: {
    renderChart(data) {
      let instance = this;
      instance.requestOptimizedTree = data;
      // let data = [1, 1, 2, 3, 5, 8, 13];
      let children = data.children;
      for (let i = 0; i < children.length; i++) {
        children[i].leaf = instance.getLeafNodes(children[i]);
        children[i].size = children[i].leaf.length;
      }
      children.sort((a, b) => b.size - a.size);
      children = children.filter(d => d.size > 5);
      instance.selectedSubTree = children;

      instance.subtreeNodes2root = {};
      instance.selectedSubTree.forEach(d => {
        let ids = instance.getAllLeafNodes(d);
        ids.forEach(id => {
          instance.subtreeNodes2root[id] = d.name;
        })
      })
      let screenWidth = document.body.clientWidth;
      let screenHeight = document.body.clientHeight;
      let width = screenWidth * 0.7,
        height = screenHeight;
      instance.chart.width = width;
      instance.chart.height = height;

      let svg = d3
        .select("#chart")
        .append("svg")
        .attr("width", width)
        .attr("height", height);
      let g_all = svg.append("g").attr("class", "all");
      let g_arc = g_all.append("g").attr("class", "arc");

      let radius = Math.min(width, height) / 2 - 80;
      instance.chart.radius = radius;

      let colors = [
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

      console.log(d3.sum(children, d => d.size));

      let arc = d3
        .arc()
        .innerRadius(radius - 10)
        .outerRadius(radius);

      let arcs = pie(children);
      instance.chart.arcs = arcs;

      g_arc
        .selectAll("path")
        .data(arcs)
        .join("path")
        .attr("fill", "steelblue")
        .attr("d", arc)
        .attr("transform", `translate(${width / 2},${height / 2})`)
        .on("click", function(d) {
          console.log(d);
        });

      instance.requestKeywords();

      // let intervalId = setInterval(() => {
      //   if (instance.nodes != null && instance.links != null) {
      //     clearInterval(intervalId);
      //     instance.nodelink(children, arcs, width, height, radius);
      //   }
      // }, 100);
    },
    nodelink(subtrees, arcs, width, height, radius) {
      let instance = this;
      let nodes = [],
        links = [];
      let ids = [];
      let nodeSet = new Set();
      this.nodes.forEach(node => {
        nodeSet.add(node.name);
      });
      arcs.forEach(d => {
        nodes.push({
          name: d.data.name,
          type: "fixed",
          x:
            // width / 2 +
            ((radius * Math.cos((d.startAngle + d.endAngle - Math.PI) / 2)) /
              4) *
            3.8,
          y:
            // height / 2 +
            ((radius * Math.sin((d.startAngle + d.endAngle - Math.PI) / 2)) /
              4) *
            3.6
        });
      });
      this.nodes.forEach(d => {
        if(instance.subtreeNodes2root[d.name]) {
          links.push({source: d.name, target: instance.subtreeNodes2root[d.name]});
        }
      })
      nodes = nodes.concat(this.nodes);
      links = links.concat(this.links);
      var nodesCopy = {};
      nodes.forEach(node => {
        nodesCopy[node.name] = JSON.parse(JSON.stringify(node));
      });

      var force = d3
        .forceSimulation()
        .force("charge", d3.forceManyBody().distanceMax(5))
        // .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collision", d3.forceCollide().radius(5))
        .on("tick", tick);

      force.nodes(nodes).force(
        "link",
        d3.forceLink(links).id(function(d) {
          return d.name;
        })
      );

      let g_all = d3.select("svg g.all");
      let g_nodelink = g_all
        .append("g")
        .attr("class", "nodelink")
        .attr("transform", `translate(${width / 2},${height / 2})`);
      var g_link = g_nodelink.selectAll(".link"),
        g_node = g_nodelink.selectAll(".node");

      g_link = g_link
        .data(links)
        .enter()
        .append("line")
        .attr("class", "link");

      g_node = g_node
        .data(nodes)
        .enter()
        .append("circle")
        .attr("class", "node")
        .attr("class", d => {
          if (d.type == "fixed") {
            return "fixedNode";
          } else {
            return "unfixedNode";
          }
        })
        .attr("r", d => {
          if (d.type == "fixed") {
            return 5;
          } else {
            return d.leaf.length > 2 ? d.leaf.length : 2;
          }
        })
        .call(
          d3
            .drag()
            .on("start", dragstart)
            .on("drag", dragged)
            .on("end", dragended)
        );

      g_node.append("title").text(d => d.name);

      function tick() {
        // console.log("tick...........");
        g_node
          .attr("cx", function(d) {
            if (d.type == "fixed") {
              d.fx = nodesCopy[d.name].x;
            }
            return d.x;
          })
          .attr("cy", function(d) {
            if (d.type == "fixed") {
              d.fy = nodesCopy[d.name].y;
            }
            return d.y;
          });
        g_link
          .attr("x1", function(d) {
            return d.source.x;
          })
          .attr("y1", function(d) {
            return d.source.y;
          })
          .attr("x2", function(d) {
            return d.target.x;
          })
          .attr("y2", function(d) {
            return d.target.y;
          });
      }

      function dragstart(d) {
        if (!d3.event.active) {
          force.alphaTarget(0.1).restart();
        }
        d.fx = d.x;
        d.fy = d.y;
      }

      function dragged(d) {
        d.fx = d3.event.x;
        d.fy = d3.event.y;
      }

      function dragended(d) {
        if (!d3.event.active) {
          force.alphaTarget(0);
        }
        d.fx = null;
        d.fy = null;
      }

      force.on("end", function() {
        console.log("end..");
      });
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
    },
    getAllLeafNodes(root) {
      let queue = [],
        ids = [];
      queue.push(root);
      while (queue.length > 0) {
        let first = queue.shift();
        if (first.children != undefined) {
          for (let i = 0; i < first.children.length; i++) {
            queue.push(first.children[i]);
            ids.push(first.children[i].name);
          }
        } else {
          ids.push(first.name);
        }
      }
      return ids;
    },
    getNodesByLayer(root, layer) {
      let queue = [],
        ids = [];
      queue.push(root);
      while (queue.length > 0) {
        let first = queue.shift();
        if (first.layer <= layer) {
          ids.push(first);
        } else {
          if (first.children) {
            for (let i = 0; i < first.children.length; i++) {
              queue.push(first.children[i]);
            }
          }
        }
      }
      return ids;
    },
    requestKeywords() {
      let instance = this;
      instance.requestDoc2keywords = [];
      let allIds = [];
      instance.selectedSubTree.forEach((element, index) => {
        let ids = instance.getLeafNodes(element);
        allIds = allIds.concat(ids);
      });
      getRequest(
        "/keywords/",
        {
          type: "doc2keywords",
          ids: allIds,
          topK: 5
        },
        function(res) {
          instance.requestDoc2keywords = res.data.keywords;
          instance.doc2keywordsMap = {};
          instance.requestDoc2keywords.forEach(d => {
            instance.doc2keywordsMap[d.id] = d.words;
          });
        }
      );
    },
    processTopic() {
      let instance = this;
      instance.topics = [];
      instance.selectedSubTree.forEach((element, index) => {
        let ids = instance.getLeafNodes(element);
        let word2count = new Map();
        ids.forEach(id => {
          instance.doc2keywordsMap[id].forEach(word => {
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
        instance.topics.push({
          key: element.name,
          wordset: objArr,
          html: html
        });
      });
    },
    processDocRelation() {
      console.log("processDocRelation...");
      let instance = this;
      let doc2keywords = {};
      let length = instance.requestDoc2keywords.length;
      let relations = [];
      for (let i = 0; i < length - 1; i++) {
        for (let j = i + 1; j < length; j++) {
          let d1 = instance.requestDoc2keywords[i];
          let d2 = instance.requestDoc2keywords[j];
          if (d1.id === d2.id) {
            continue;
          }
          let intersection = _.intersection(d1.words, d2.words);
          if (intersection.length > 0) {
            relations.push({
              source: d1.id,
              target: d2.id,
              words: intersection
            });
          }
        }
      }
      instance.relations = relations;
    },
    processGraphData() {
      let instance = this;
      instance.nodes = [];
      instance.selectedSubTree.forEach(tree => {
        instance.nodes = instance.nodes.concat(instance.getNodesByLayer(tree, 5));
      })
      for (let i = 0; i < instance.nodes.length; i++) {
        if (!instance.nodes[i].leaf) {
          instance.nodes[i].leaf = instance.getLeafNodes(instance.nodes[i]);
        }
        instance.nodes[i].keywords = [];
        instance.nodes[i].leaf.forEach(v => {
          instance.nodes[i].keywords = instance.nodes[i].keywords.concat(
            instance.doc2keywordsMap[+v]
          );
        });
        instance.nodes[i].keywords = Array.from(
          new Set(instance.nodes[i].keywords)
        );
      }
      instance.links = [];
      for (let i = 0; i < instance.nodes.length - 1; i++) {
        for (let j = i + 1; j < instance.nodes.length; j++) {
          let d1 = instance.nodes[i];
          let d2 = instance.nodes[j];
          if (d1.name === d2.name) {
            continue;
          }
          let intersection = _.intersection(d1.keywords, d2.keywords);
          if (intersection.length > 1) {
            instance.links.push({
              source: d1.name,
              target: d2.name,
              words: intersection
            });
          }
        }
      }
      instance.nodelink(
        instance.selectedSubTree,
        instance.chart.arcs,
        instance.chart.width,
        instance.chart.height,
        instance.chart.radius
      );
    }
  },
  watch: {
    requestDoc2keywords: {
      handler(n, o) {
        try {
          this.processTopic();
          this.processGraphData();
        } catch (error) {}
      },
      deep: true
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

    /deep/ .fixedNode {
      fill: grey;
    }

    /deep/ .unfixedNode {
      fill: slateblue;
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