Page({
  onStart() {
    wx.navigateTo({
      url: '/pages/topicSelection/topicSelection',
    });
  }
  
});
// 在需要使用JSON数据的地方
const fs = wx.getFileSystemManager();
// 读取本地JSON文件
fs.readFile({
filePath: '/pages/role.json', // 替换为你的JSON文件路径
encoding: 'utf8', // 指定编码方式
success: (res) => {
// 解析JSON数据
const jsonData = JSON.parse(res.data);
// 在这里可以使用jsonData进行后续操作
},
fail: (err) => {
console.log('读取JSON文件失败:', err);
}
});
