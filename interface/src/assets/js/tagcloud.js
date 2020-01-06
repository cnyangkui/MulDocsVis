/***
 * 可调节参数，欢迎来调
 ***/

const inputWords = 'hello world 你好 世界 呵呵哒' // 显示Text
const MinBoxSize = 5 // 最小网格大小

const fontFamily = 'sans-serif' // 字体样式
const fontSize = 15 // 字体大小
const wordW = 15 // 宽度
const wordH = 15 // 高度
// console.log(d3)
// 层次边界树
class HierarchyTree {

  constructor (x0, y0, x1, y1) {
    this.x0 = x0
    this.y0 = y0
    this.x1 = x1
    this.y1 = y1
    this.children = []
  }

  // 添加孩子节点
  addChildren (children) {
    this.children = [].concat(this.children, children)
  }
}

// 初始化层次树
const initTree = (d) => {
  let initBBox = {x0: 0, y0: 0, x1: wordW*d.split('').length, y1: wordH}
  return cosntructTree({wordPixelArr: getWordPixelArr(d), ...initBBox}, initBBox)
}

// 构建单词的层次树
const cosntructTree = (wordPixel, bbox) => {
  let {x0, y0, x1, y1} = bbox
  // 检测指定bbox是否包含在单词内容里
  if (isTargetBoxInWord(wordPixel, bbox)) {
    // debugger
    return new HierarchyTree(x0, y0, x1, y1)
  } else if (isTargetBoxIntersectsWord(wordPixel, bbox)) {
    // 如果单词和BBox有交叉
    // debugger
    let tree = new HierarchyTree(x0, y0, x1, y1)

    if (x1 - x0 > MinBoxSize || y1 - y0 > MinBoxSize) {
      let cx = ~~((x0 + x1) / 2)
      let cy = ~~((y0 + y1) / 2)
      let tl = cosntructTree(wordPixel, {x0, y0, x1: cx, y1: cy})
      let tr = cosntructTree(wordPixel, {x0: cx, y0, x1, y1: cy})
      let bl = cosntructTree(wordPixel, {x0, y0: cy, x1: cx, y1})
      let br = cosntructTree(wordPixel, {x0: cx, y0: cy, x1, y1})

      tl && tree.addChildren(tl)
      tr && tree.addChildren(tr)
      bl && tree.addChildren(bl)
      br && tree.addChildren(br)
    }
    return tree
  }
  return null
}

// 检测bbox是否包含在单词形状里
const isTargetBoxInWord = (wordPixel, bbox) => {
  let {x0, y0, x1, y1} = bbox
  // debugger
  // 如果bbox直接都不在单词的bbox内，那一定不会在单词的形状内
  if (x0 < wordPixel.x0 || y0 < wordPixel.y0 || x1 >= wordPixel.x1 || y1 >= wordPixel.y1) return false

  x0 -= wordPixel.x0
  y0 -= wordPixel.y0
  x1 -= wordPixel.x0
  y1 -= wordPixel.y0

  let w = wordPixel.x1 - wordPixel.x0
  let wordPixelArr = wordPixel.wordPixelArr

  for (let i = x0; i < x1; i++) {
    for (let j = y0; j < y1; j++) {
      if (!wordPixelArr[j * w + i]) return false
    }
  }
  return true
}

// 检测bbox和单词是否交叉
const isTargetBoxIntersectsWord = (wordPixel, bbox) => {
  let {x0, y0, x1, y1} = bbox
  // debugger

  x0 = Math.max(0, x0 - wordPixel.x0)
  y0 = Math.max(0, y0 - wordPixel.y0)
  x1 = Math.min(wordPixel.x1, x1) - wordPixel.x0
  y1 = Math.min(wordPixel.y1, y1) - wordPixel.y0

  let w = wordPixel.x1 - wordPixel.x0
  let wordPixelArr = wordPixel.wordPixelArr
  for (let j = y0; j < y1; j++) {
    for (let i = x0; i < x1; i++) {
      if (wordPixelArr[j * w + i]) return true
    }
  }
  return false
}

// 检测两棵树是否重叠
const treesOverlap = (treeA, treeB, posA, posB) => {
  let [ax, ay] = posA
  let [bx, by] = posB
  if (bboxOverlap(treeA, treeB, posA, posB)) {
    if (!treeA.children.length) {
      if (!treeB.children.length) return true
      else for (let i = 0, n = treeB.children.length; i < n; i++) {
        if (treesOverlap(treeA, treeB.children[i], posA, posB)) return true
      }
    } else for (let i = 0, n = treeA.children.length; i < n; i++) {
      if (treesOverlap(treeB, treeA.children[i], posB, posA)) return true
    }
  }
  return false
}

// 检测两个边界bbox是否重叠
const bboxOverlap = (a, b, posA, posB) => {
  let [ax, ay] = posA
  let [bx, by] = posB
  return a.x1 + ax > b.x0 + bx && ax + a.x0 < bx + b.x1 && ay + a.y1 > by + b.y0 && ay + a.y0 < by + b.y1
}

// 冲突检测：检测是否存在有重叠的单词
const wordsCollide = (wordsList) => {
  let len = wordsList.length
  let collideIndex = {}
  for (let i = 0; i < len; i++) {
    for (let j = i + 1; j < len; j++) {
      let a = wordsList[i]
      let b = wordsList[j]

      let isCollide = treesOverlap(a.tree, b.tree, a.pos, b.pos)

      collideIndex[i] = isCollide || collideIndex[i]
      collideIndex[j] = isCollide || collideIndex[j]
    }
  }

  let wordsCollide = []
  wordsList.forEach((d, i) => {
    collideIndex[i] && wordsCollide.push(d.word)
    // d3.select('.word-' + i).classed('collide', collideIndex[i])
  })

  console.log(wordsCollide.length ? '重叠的节点是：[' + wordsCollide.join(', ') + ']' : '暂无重叠节点')
  if(wordsCollide) return true;
  else return false;
}

// 扁平化树结构
// const flatten = (root) => {
//   let nodes = []
//   root.depth = 0

//   traverse(root)

//   return nodes
//   function traverse (node) {
//     let depth = node.depth + 1
//     if (node.children) {
//       node.children.forEach((d) => {
//         d.depth = depth
//         traverse(d)
//       })
//     }
//     nodes.push(node)
//   }
// }

// 获取单词的像素值
function getWordPixelArr (text) {
  let len = text.split('').length;
  console.log(len);
  let canvas = document.createElement('canvas')
  canvas.width = wordW*len
  canvas.height = wordH
  let c = canvas.getContext('2d')
  c.strokeStyle = '#f00'
  c.clearRect(0, 0, wordW * 2 * len, wordH * 2)
  c.save()
  c.textAlign = 'center'
  c.font = ~~fontSize + 'px ' + fontFamily

  c.translate((wordW*len) / 2, (wordH + fontSize) / 2)

  c.fillText(text, 0, 0)

  c.restore()
  // imageData 中包含width、height、data
  // 其中data为Uint8ClampedArray，是一个长度为width*height长度的一维数组，描述各个像素的rgba
  let imageData = c.getImageData(1, 1, wordW*len, wordH)
  let pixels = imageData.data

  let arr = []

  // 如果这个像素内的r+g+b+a不为0，则表示该像素有内容
  // console.log(wordW*len, wordH)
  console.log(pixels)
  for (let i = 0; i < wordW * wordH * len; i++) {
    arr[i] = pixels[i * 4 + 0] + pixels[i * 4 + 1] + pixels[i * 4 + 2] + pixels[i * 4 + 3]
  }
  console.log(arr)
  return arr
}

export {initTree, wordsCollide}
// // 生成并绘制Text及层次树
// const showWordHierarchyTree = (inputWords) => {
//   let gap = 10
//   // 生成文字及其层次树
//   let wordsList = inputWords.split(' ').map((d, i) => {
//     return {
//       word: '' + d,
//       tree: initTree(d),
//       pos: [i * (wordW * ('' + d).split('').length + gap), 0]
//     }
//   })

//   let g = svg.selectAll('g').data(wordsList)

//   let wordG = g.enter().append('g')
//   .attr('class', (d, i) => 'word-' + i)
//   .attr('transform', d => 'translate(' + d.pos + ')')

//   // 绘制文字
//   wordG
//   .append('text')
//   .attr('x',d => wordW*d.word.split('').length / 2)
//   .attr('y', (wordH + fontSize) / 2)
//   .attr('text-anchor', 'middle')
//   .attr('font-size', fontSize)
//   .attr('font-family', fontFamily)
//   .text(d => d.word)

//   wordG.call(d3.drag()
//     .on('drag', function (d) {
//       d.pos = [Math.max(0, d3.event.x - wordW*(d.word.split('').length) / 2), Math.max(0, d3.event.y - wordH / 2)]

//       d3.select(this).attr('transform', d => 'translate(' + d.pos + ')')

//       wordsCollide(wordsList)
//     })
//   )

//   // 绘制Box
//   let hbbox = wordG.selectAll('rect').data(d => flatten(d.tree))
//   hbbox.exit().remove()

//   hbbox.enter().append('rect')
//   .attr('width', d => d.x1 - d.x0)
//   .attr('height', d => d.y1 - d.y0)
//   .attr('x', d => d.x0)
//   .attr('y', d => d.y0)
//   .attr('fill', 'none')
// }

// // 测试程序


// let svg = d3.select('#HTree').append('svg')
// .attr('width', '100%')
// .attr('height', '100%')
// .attr('pointer-events', 'all')
// .append('g')
// .attr('transform', 'translate(5, 5)')

// showWordHierarchyTree(inputWords)
