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
        keywords: null,
        doc2keywords: null,
      },
      docNum: 5,
      wordlist: []
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
      instance.requestData.optimizedTree = data;
      // let data = [1, 1, 2, 3, 5, 8, 13];
      let children = data.children;
      for (let i = 0; i < children.length; i++) {
        children[i].leaf = instance.getLeafNodes(children[i]);
        children[i].size = children[i].leaf.length;
      }
      children.sort((a, b) => b.size - a.size);
      children = children.filter(d => d.size > 5);
      instance.processedData.selectedSubTree = children;

      let screenWidth = document.body.clientWidth;
      let screenHeight = document.body.clientHeight;
      let width = screenWidth * 0.7,
        height = screenHeight;

      let svg = d3
        .select("#chart")
        .append("svg")
        .attr("width", width)
        .attr("height", height);
      let g_all = svg.append("g").attr("class", "all");
      let g_arc = g_all.append("g").attr("class", "arc");

      let radius = Math.min(width, height) / 2 - 30;

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

      let g_nodes = g_all.append("g").attr("class", "ddd");
      g_nodes
        .selectAll("circle")
        .data(arcs)
        .enter()
        .append("circle")
        .attr("r", 2)
        .attr("cx", function(d) {
          return (
            width / 2 +
            ((radius * Math.cos((d.startAngle + d.endAngle - Math.PI) / 2)) /
              4) *
              3
          );
        })
        .attr("cy", function(d) {
          return (
            height / 2 +
            ((radius * Math.sin((d.startAngle + d.endAngle - Math.PI) / 2)) /
              4) *
              3
          );
        });

      instance.requestKeywords();

      // instance.nodelink(children, arcs, width, height, radius);
    },
    nodelink(subtrees, arcs, width, height, radius) {
      console.log(arcs.length);
      let nodes = [],
        links = [];
      let ids = [];
      arcs.forEach(d => {
        nodes.push({
          id: d.data.name,
          type: "fixed",
          x:
            // width / 2 +
            ((radius * Math.cos((d.startAngle + d.endAngle - Math.PI) / 2)) /
              4),
          y:
            // height / 2 +
            ((radius * Math.sin((d.startAngle + d.endAngle - Math.PI) / 2)) /
              4) 
        });
        d.data.leaf.forEach(v => {
          ids.push(v);
          nodes.push({ id: v, type: "unfixed" });
          links.push({ source: d.data.name, target: v });
        });
      });
      console.log(ids);
      getRequest(
        "/similarity/",
        {
          type: "group",
          ids: ids,
          threshold: 0.5
        },
        function(res) {
          links = links.concat(res.data.similarity);
          // console.log(links.length);
          // console.log(res.data.similarity.length);

          var nodesCopy = {};
          nodes.forEach(node => {
            nodesCopy[node.id] = JSON.parse(JSON.stringify(node));
          });

          var force = d3
            .forceSimulation()
            .force("charge", d3.forceManyBody())
            // .force("center", d3.forceCenter(width / 2, height / 2))
            .on("tick", tick);

          force.nodes(nodes).force(
            "link",
            d3.forceLink(links).id(function(d) {
              return d.id;
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
            .attr("r", 5)
            .call(
              d3
                .drag()
                .on("start", dragstart)
                .on("drag", dragged)
                .on("end", dragended)
            );

          g_node.append("title").text(d => d.id);

          function tick() {
            console.log("tick...........");
            g_node
              .attr("cx", function(d) {
                if (d.type == "fixed") {
                  d.fx = nodesCopy[d.id].x;
                }
                return d.x;
              })
              .attr("cy", function(d) {
                if (d.type == "fixed") {
                  d.fy = nodesCopy[d.id].y;
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
          // links = links.concat(res.data);
          // console.log(links.length)
        }
      );
    },
    getNodeLinkData(subtrees) {},
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
    requestKeywords() {
      let instance = this;
      instance.processedData.keywords = [];
      instance.processedData.doc2keywords = [];
      instance.processedData.selectedSubTree.forEach((element, index) => {
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
            instance.processedData.doc2keywords = instance.processedData.doc2keywords.concat(res.data.keywords);
          }
        );
      });
      // console.log(instance.processedData.doc2keywords)
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