<template>
  <div class="tree-container">
    <div id="tree"></div>
    <div id="control"></div>
  </div>
</template>
<script>
import * as d3 from "d3";
import treedata from "../assets/data/tree.json";
export default {
  name: "HierarchicalTree",
  data() {
    return {};
  },
  mounted() {
    this.renderTree();
  },
  methods: {
    renderTree() {
      let screenWidth = document.body.clientWidth;
      let screenHeight = document.body.clientHeight;
      let width = screenWidth * 0.8,
        height = screenHeight;
      let svg = d3
        .select("#tree")
        .append("svg")
        .attr("width", width)
        .attr("height", height);
      let g = svg.append("g").attr("transform", `translate(${width/2},${height/2})`);
      let cluster = d3.cluster().size([2 * Math.PI, width / 2 - 150]);

      svg
        .append("rect")
        .attr("width", width)
        .attr("height", height)
        .style("fill", "none")
        .style("pointer-events", "all")
        .call(
          d3
            .zoom()
            // .scaleExtent([1 / 2, 4])
            .on("zoom", zoomed)
        );

      function zoomed() {
        g.attr("transform", d3.event.transform);
      }

      var hierarchy = d3.hierarchy(treedata);
      cluster(hierarchy);
      var descendants = hierarchy.descendants();
      console.log(descendants);
      // fontSize.domain(
      //   d3.extent(descendants, function(d) {
      //     return d.depth;
      //   })
      // );

      g
        .append("g")
        .attr("fill", "none")
        .attr("stroke", "#555")
        .attr("stroke-opacity", 0.4)
        .attr("stroke-width", 1.5)
        .selectAll("path")
        .data(hierarchy.links())
        .join("path")
        .attr(
          "d",
          d3
            .linkRadial()
            .angle(d => d.x)
            .radius(d => d.y)
        );

      g
        .append("g")
        .selectAll("circle")
        .data(hierarchy.descendants())
        .join("circle")
        .attr(
          "transform",
          d => `
        rotate(${(d.x * 180) / Math.PI - 90})
        translate(${d.y},0)
      `
        )
        .attr("fill", d => (d.children ? "#555" : "#999"))
        .attr("r", 2.5);

      g
        .append("g")
        .attr("font-family", "sans-serif")
        .attr("font-size", 10)
        .attr("stroke-linejoin", "round")
        .attr("stroke-width", 3)
        .selectAll("text")
        .data(hierarchy.descendants().filter(d => d.children == undefined))
        .join("text")
        .attr(
          "transform",
          d => `
        rotate(${(d.x * 180) / Math.PI - 90}) 
        translate(${d.y},0) 
        rotate(${d.x >= Math.PI ? 180 : 0})
      `
        )
        .attr("dy", "0.31em")
        .attr("x", d => (d.x < Math.PI === !d.children ? 6 : -6))
        .attr("text-anchor", d =>
          d.x < Math.PI === !d.children ? "start" : "end"
        )
        .text(d => d.data.name)
        .clone(true)
        .lower()
        .attr("stroke", "white");
    }
  }
};
</script>
<style lang="scss" scoped>
* {
  border: 1px solid red;
}
.tree-container {
  width: 100%;
  height: 100%;

  #tree {
    width: 80%;
    height: 100%;
    float: left;
    
    /deep/ text {
      font-family: "Open Sans", sans-serif;
      pointer-events: none;
    }
    /deep/ circle {
      fill: steelblue;
      opacity: 0.4;
    }
  }
  #control {
    width: 20%;
    // height: 100%;
    float: left;
  }
}
</style>