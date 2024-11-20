Page({
  data: {
    topics: [], // 主题列表
    selectedTopic: null, // 选中的主题
  },

  onLoad() {
    // 初始化主题列表
    this.setData({
      topics: [
        { name: "执政之道", selected: false },
        { name: "道德修养", selected: false },
        { name: "美与艺术", selected: false },
        { name: "孝道的理解", selected: false },
        { name: "道德与礼仪", selected: false },
        { name: "学习与志向", selected: false },
        { name: "君子的修养", selected: false },
        { name: "仁爱与智慧", selected: false },
        { name: "对友谊的看法", selected: false },
        { name: "社会和谐", selected: false },
        { name: "对生死的看法", selected: false },
        { name: "以德治国", selected: false },
        { name: "贤者的品质", selected: false },
        { name: "教育与教导", selected: false },
        // 可添加更多主题
      ],
    });
  },

  toggleTopic(e) {
    const index = e.currentTarget.dataset.index;

    // 更新主题状态
    const updatedTopics = this.data.topics.map((topic, i) => ({
      ...topic,
      selected: i === index, // 仅当前索引为 true，其余为 false
    }));

    this.setData({
      topics: updatedTopics,
      selectedTopic: updatedTopics[index].selected ? updatedTopics[index].name : null,
    });
  },

  confirmSelection() {
    // 确保已选择主题
    if (!this.data.selectedTopic) {
      wx.showToast({
        title: "请选择一个主题",
        icon: "none",
      });
      return;
    }

    // 跳转到功能选择页面，传递主题数据
    wx.navigateTo({
      url: `/pages/functionSelection/functionSelection?theme=${encodeURIComponent(this.data.selectedTopic)}`,
    });
  },
});
