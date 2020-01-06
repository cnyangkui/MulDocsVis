const d3 = require("d3")
// import projdata from '../../../public/data/output/thucnews/projection_dense_tfidf.json'
// import similarityMatrix from '../../../public/data/output/thucnews/similarity_matrix_5round.json'

/**
 * 获得在2D平面距离超过一定阈值，但是相似度较高文档对。这些文档比较相似，但是在2D平面相距较远
 * @param {Array} projdata [{index: number, text: string, x: number, y: number}, ...] 投影数据 
 * @param {Array} similarityMatrix 二维数组, 存储所有文档对的相似度 
 * @param {number} dist_quantile float 距离分位数阈值, 过滤获得距离大于该分位数的文档对
 * @param {number} similarity_threshold float 相似度阈值, 过滤获得相似度大于该值的文档对
 * @returns {Array} [doc1-doc2, ...] 每个元素是一个字符串，使用文档索引和“-”连接起来
 */
function getLongdisHighsimilarity(projdata, similarityMatrix, dist_quantile=0.3, similarity_threshold=0.2) {
  let dist2similarity = []
  for(let i=0,len1=similarityMatrix.length; i<len1; i++) {
    for(let j=i+1,len2=similarityMatrix[i].length; j<len2; j++) {
      dist2similarity.push({
        pair: i+'-'+j,
        similarity: similarityMatrix[i][j],
        dist: Math.sqrt((projdata[i].x-projdata[j].x)**2 + (projdata[i].y-projdata[j].y)**2)
      })
    }
  }
  dist2similarity = dist2similarity.sort((a, b) => a.dist - b.dist);
  let dist_threshold = d3.quantile(dist2similarity, dist_quantile, d => d.dist)
  let filter = dist2similarity.filter((d, i) => d.dist > dist_threshold && d.similarity > similarity_threshold);
  return filter;
}


module.exports = getLongdisHighsimilarity;