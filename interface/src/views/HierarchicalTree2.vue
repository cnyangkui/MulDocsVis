<template>
  <div class="tree-container">
    <div id="tree"></div>
    <div id="control">
      <el-tabs v-model="activeName" type="card" @tab-click="requestData">
        <el-tab-pane label="关键词" name="keywords">
          <div class="words-panel">
            <div v-if="docData.keywords">
              <div v-html="docData.keywords.html"></div>
              <el-divider></el-divider>
              <div v-for="item of docData.keywords.list" :key="item.id">
                <strong>{{item.id}}</strong>
                <el-divider direction="vertical"></el-divider>
                <span>{{item.words.toString()}}</span>
                <el-divider></el-divider>
              </div>
            </div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="公共关键词" name="commonKeywords">
          <div class="words-panel">
            <p
              v-for="item of docData.commonKeywords"
              :key="item.key"
              style="margin-bottom:0px;"
            >{{item.key + " " + item.value}}</p>
          </div>
        </el-tab-pane>
        <el-tab-pane label="公共普通词" name="commonWords">
          <div class="words-panel">
            <p
              v-for="item of docData.commonWords"
              :key="item.key"
              style="margin-bottom:0px;"
            >{{item.key + " " + item.value}}</p>
          </div>
        </el-tab-pane>
      </el-tabs>
      <div v-if="docData.texts && docData.texts.length != 0" class="docs-panel">
        <div v-for="item of docData.texts" :key="item.key" class="doc-panel">
          <div v-html="item.html || item.value"></div>
        </div>
      </div>
    </div>
    <el-dialog :title="'文档ID：'+currentDocId" :visible.sync="dialogVisible" width="85%">
      <span>{{doctext}}</span>
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="dialogVisible = false">确定</el-button>
      </span>
    </el-dialog>
  </div>
</template>
<script>
import * as d3 from "d3";
import { getRequest } from "../assets/js/api.js";
export default {
  name: "HierarchicalTree",
  data() {
    return {
      activeName: "keywords",
      docData: {
        keywords: null,
        commonKeywords: null,
        commonWords: null,
        texts: null
      },
      currentDocId: null,
      wordtype: "keywords",
      wordlist: [],
      ids: [],
      topK: 20,
      color: null,
      dialogVisible: false,
      doctext: null,
      clickTimeId: null //单击延时触发
    };
  },
  mounted() {
    let instance = this;
    getRequest("/htree", {}, function(res) {
      console.log(res.data);
      instance.renderTree(res.data);
    });
  },
  methods: {
    renderTree(treedata) {
      let instance = this;
      let screenWidth = document.body.clientWidth;
      let screenHeight = document.body.clientHeight;
      let width = screenWidth * 0.7,
        height = screenHeight;
      let duration = 750;

      let svg = d3
        .select("#tree")
        .append("svg")
        .attr("width", width)
        .attr("height", height);

      // 绘制颜色矩形块
      let colorlevel = ["#FF1A00", "#FF9900", "#E6FF00", "#66FF00", "#00A779"];
      this.color = d3
        .scaleQuantize()
        .domain([0, 1])
        .range(colorlevel);
      let colorbar = svg.append("g");
      let colorRectWidth = 20,
        colorRectHeight = 20;
      colorbar
        .selectAll("rect")
        .data(colorlevel)
        .enter()
        .append("rect")
        .attr("x", (d, i) => i * colorRectWidth)
        .attr("y", 0)
        .attr("width", colorRectWidth)
        .attr("height", colorRectHeight)
        .attr("fill", (d, i) => colorlevel[i])
        .attr("stroke", "black");

      // 缩放
      let g = svg.append("g");
      svg.call(d3.zoom().on("zoom", zoomed)).on("dblclick.zoom", null);
      function zoomed() {
        g.attr("transform", d3.event.transform);
      }

      // 开始绘制 Radinal Dendrogram
      var root = d3.hierarchy(treedata);
      root.x0 = 0;
      root.y0 = 0;
      root.category = "nonleaf";
      root.children.forEach(collapse);
      let cluster = d3.cluster().size([2 * Math.PI, height / 2 - 50]);

      update(root);

      // console.log(root);

      // Collapse the node and all it's children
      function collapse(d) {
        if (d.children) {
          d._children = d.children;
          d._children.forEach(collapse);
          // d.children = null;
          d.category = "nonleaf";
        } else {
          d.category = "leaf";
        }
      }

      function update(source) {
        let clusterData = cluster(root);
        let nodes = clusterData.descendants(),
          links = clusterData.descendants().slice(1);
        // ****************** links section ***************************

        // Update the links...
        let link = g.selectAll("path.link").data(links, function(d) {
          return d.id;
        });

        // Enter any new links at the parent's previous position.
        let linkEnter = link
          .enter()
          .append("path")
          .attr("class", "link")
          .attr("stroke", "grey")
          .attr("stroke-width", 0.5)
          .attr("d", function(d) {
            let o = { x: source.x0, y: source.y0 };
            return diagonal(o, o);
          });

        // UPDATE
        let linkUpdate = linkEnter
          .merge(link)
          .transition()
          .duration(duration)
          .attr("d", function(d) {
            return diagonal(d, d.parent);
          });

        // Remove any exiting links
        var linkExit = link
          .exit()
          .transition()
          .duration(duration)
          .attr("d", function(d) {
            let o = { x: source.x, y: source.y };
            return diagonal(o, o);
          })
          .remove();

        // ****************** Nodes section ***************************

        // Update the nodes...
        let node = g.selectAll("g.node").data(nodes, function(d) {
          return d.id || (d.id = d.data.name);
        });

        // Enter any new modes at the parent's previous position.
        let nodeEnter = node
          .enter()
          .append("g")
          .attr("class", d => "node node-" + d.data.name)
          .attr("transform", function(d) {
            return "translate(" + project(source.x0, source.y0) + ")";
          })
          .on("click", function(d) {
            // 取消上次延时未执行的方法
            clearTimeout(instance.clickTimeId);
            //执行延时
            instance.clickTimeId = setTimeout(function() {
              //此处为单击事件要执行的代码
              if (d.children) {
                d._children = d.children;
                d.children = null;
              } else {
                d.children = d._children;
                d._children = null;
              }
              update(d);
            }, 250);
          });

        // Add labels for the nodes
        nodeEnter
          .filter(x => x.children == undefined)
          .append("text")
          .text(function(d) {
            return d.data.name;
          })
          .attr("stroke", "black")
          .attr("stroke-width", 0.1)
          .attr("font-size", function(d) {
            return "2px";
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
          .attr("alignment-baseline", "central");

        // Add Circle for the nodes
        nodeEnter
          .append("circle")
          .attr("r", 2)
          .attr("fill", function(d) {
            if (d.category == "leaf") {
              return "white"; //"#00EBEB";
            } else {
              return instance.color(d.data.distance); // d._children ? instance.color(d.data.distance) : "black";
            }
          })
          .attr("stroke", "grey")
          .attr("stroke-width", 0.5)
          .attr("opacity", 0.5)
          .on("dblclick", function(d, i) {
            d3.select(`.node-${instance.currentDocId}`)
              .selectAll("circle")
              .classed("magnifyingCircle", false);
            d3.select(this).classed("magnifyingCircle", true);
            // 取消上次延时未执行的方法
            clearTimeout(instance.clickTimeId);
            instance.currentDocId = d.data.name;
            instance.ids = instance.getLeafNodes(d);
            instance.docData.keywords = null;
            instance.docData.commonKeywords = null;
            instance.docData.commonWords = null;
            instance.docData.texts = null;
            instance.requestData();
            instance.requestDocs();
          });

        // Transition nodes to their new position.
        let nodeUpdate = nodeEnter
          .merge(node)
          .transition()
          .duration(duration)
          .attr("fill", function(d) {
            if (d.category == "leaf") {
              return "white"; //"#00EBEB";
            } else {
              return d._children ? instance.color(d.data.distance) : "black";
            }
          })
          .attr("transform", function(d) {
            return "translate(" + project(d.x, d.y) + ")";
          });

        // Remove any exiting nodes
        let nodeExit = node
          .exit()
          .transition()
          .duration(duration)
          .attr("transform", function(d) {
            return "translate(" + project(source.x, source.y) + ")";
          })
          .remove();

        // On exit reduce the node circles size to 0
        nodeExit.select("circle").attr("r", 0);

        // On exit reduce the opacity of text labels
        nodeExit.select("text").style("fill-opacity", 0);

        // Store the old positions for transition.
        nodes.forEach(function(d) {
          d.x0 = d.x;
          d.y0 = d.y;
        });
        // root.eachBefore(d => {
        //   d.x0 = d.x;
        //   d.y0 = d.y;
        // });

        // Creates a curved (diagonal) path from parent to the child nodes
        function diagonal(s, d) {
          return (
            "M" +
            project(s.x, s.y) +
            "C" +
            project(s.x, (s.y + d.y) / 2) +
            " " +
            project(d.x, (s.y + d.y) / 2) +
            " " +
            project(d.x, d.y)
          );
        }
      }

      function project(theta, r) {
        return [
          width / 2 + r * Math.sin(theta),
          height / 2 + r * Math.cos(theta) + 4
        ];
      }
    },
    search() {
      let docid = parseInt(this.currentDocId);
      let instance = this;
      d3.select("svg")
        .selectAll("circle")
        // .attr("fill", function(d, i) {
        //   if (d.data.name == docid) {
        //     return "red";
        //   } else {
        //     if(d.children == undefined) {
        //       return "#00EBEB";
        //     } else {
        //       return instance.color(d.data.distance);
        //     }
        //   }
        // })
        .attr("r", function(d) {
          if (d.data.name == docid) {
            return 10;
          } else {
            return 2;
          }
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
          ids.push(first.data.name);
        }
      }
      return ids;
    },
    getDoc() {
      if (this.currentDocId == null) {
        return;
      }
      let instance = this;
      this.dialogVisible = true;
      getRequest(
        "/documents/",
        {
          type: "single",
          id: instance.currentDocId
        },
        function(res) {
          instance.doctext = res.data.text;
        }
      );
    },
    requestData() {
      let instance = this;
      switch (instance.activeName) {
        case "commonKeywords":
          getRequest(
            "/keywords/",
            {
              type: "multiple",
              ids: instance.ids,
              topK: 50
            },
            function(res) {
              instance.docData.commonKeywords = res.data.keywords.map(
                (d, i) => {
                  return { key: i, value: d };
                }
              );
            }
          );
          break;
        case "keywords":
          getRequest(
            "/keywords/",
            {
              type: "doc2keywords",
              ids: instance.ids,
              topK: 20
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
              instance.docData.keywords = {
                key: instance.currentDocId,
                list: res.data.keywords,
                set: objArr,
                html: html
              };
              console.log(instance.docData.keywords);
            }
          );
          break;
        case "commonWords":
          getRequest(
            "/commonwords/",
            {
              ids: instance.ids
            },
            function(res) {
              instance.docData.commonWords = res.data.commonWords.map(
                (d, i) => {
                  return { key: i, value: d };
                }
              );
            }
          );
          break;
        default:
          break;
      }
    },
    requestDocs() {
      let instance = this;
      getRequest(
        "/documents/",
        {
          ids: instance.ids
        },
        function(res) {
          if (instance.docData.keywords == null) {
            let intervalId = setInterval(() => {
              if (instance.docData.keywords != null) {
                clearInterval(intervalId);
                instance.docData.texts = res.data.texts.map((d, i) => {
                  let html = d.content;
                  instance.docData.keywords.set.forEach(keyword => {
                    let reg = new RegExp("(" + keyword[0] + ")", "g");
                    html = html.replace(
                      reg,
                      "<span style='background-color:yellow;'>" +
                        keyword[0] +
                        "</span>"
                    );
                  });
                  return { key: d.did, value: d.content, html: html };
                });
              }
            }, 100);
          } else {
            instance.docData.texts = res.data.texts.map((d, i) => {
              let html = `<strong>${d.did}</strong>
            <el-divider direction="vertical"></el-divider>${d.content}`;
              instance.docData.keywords.set.forEach(keyword => {
                let reg = new RegExp("(" + keyword[0] + ")", "g");
                html = html.replace(
                  reg,
                  "<span style='background-color:yellow;'>" +
                    keyword[0] +
                    "</span>"
                );
              });
              return { key: d.did, value: d.content, html: html };
            });
          }
        }
      );
    }
  },
  watch: {
    wordtype(n, o) {
      this.getWords();
    },
    topK(n, o) {
      this.getWords();
    },
    activeName(n, o) {
      this.requestData();
    }
  },
  computed: {}
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

    /deep/ .magnifyingCircle {
      r: 8;
    }
  }
  #control {
    width: 30%;
    height: 100%;
    float: left;
    // border: 1px solid grey;

    .words-panel {
      height: 300px;
      overflow-y: auto;
      margin-bottom: 10px;
      // border: 1px solid grey;
    }
    .docs-panel {
      height: 600px;
      overflow-y: auto;

      .doc-panel {
        height: 300px;
        overflow-y: auto;
        margin-bottom: 5px;
        border: 1px solid gray;
      }
    }
  }
}
</style>