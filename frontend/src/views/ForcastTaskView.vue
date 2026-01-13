<template>
  <ContentComponent>
    <div class="task-container">
      <div class="card">
        <div class="card-header">
          <h5 class="mb-0">时序预测任务</h5>
        </div>
        <div class="card-body">
          <!-- 控制面板 -->
          <div class="control-panel mb-4">
            <div class="row align-items-center">
              <div class="col-md-3">
                <div class="input-group">
                  <span class="input-group-text">数据集</span>
                  <select v-model="selectedDataset" class="form-select" @change="handleDatasetChange">
                    <option v-for="dataset in datasets" :key="dataset" :value="dataset">
                      {{ dataset }}
                    </option>
                  </select>
                </div>
              </div>
              <div class="col-md-3">
                <div class="input-group">
                  <span class="input-group-text">维度</span>
                  <select v-model="selectedDimension" class="form-select" @change="updateChart">
                    <option v-for="dim in dimensions" :key="dim" :value="dim">
                      维度 {{ dim + 1 }}
                    </option>
                  </select>
                </div>
              </div>
              <div class="col-md-3">
                <div class="form-check form-switch">
                  <input class="form-check-input" type="checkbox" v-model="showPrediction" 
                         @change="updateChart" id="showPrediction">
                  <label class="form-check-label" for="showPrediction">
                    显示预测结果
                  </label>
                </div>
              </div>
              <div class="col-md-3">
                <button class="btn btn-primary" @click="predictData" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  {{ loading ? '预测中...' : '开始预测' }}
                </button>
              </div>
            </div>
          </div>

          <!-- 加载状态提示 -->
          <div v-if="loading" class="row mb-4">
            <div class="col-12">
              <div class="alert alert-info">
                <i class="fas fa-spinner fa-spin me-2"></i>
                正在加载数据，请稍候...
              </div>
            </div>
          </div>

          <!-- 数据统计信息 -->
          <div v-if="historyData.length > 0 && !loading" class="row mb-4">
            <h6 class="mb-3">数据统计信息 - {{ selectedDataset }}</h6>
            <div class="col-3" v-for="stat in dataStats" :key="stat.id">
              <div class="stat-card" :style="{ borderLeft: `4px solid ${stat.color}` }">
                <div class="stat-header">
                  <div class="stat-icon" :style="{ backgroundColor: stat.color + '20' }">
                    <i :class="stat.icon"></i>
                  </div>
                  <span class="stat-title">{{ stat.title }}</span>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ stat.value }}</div>
                  <div class="stat-unit">{{ stat.unit }}</div>
                </div>
                <div class="stat-desc">{{ stat.description }}</div>
              </div>
            </div>
          </div>

          <!-- 图表区域 -->
          <div class="row">
            <div class="col-12">
              <div class="chart-container">
                <div v-if="!hasData" class="no-data">
                  <i class="fas fa-chart-line fa-3x mb-3 text-muted"></i>
                  <p class="mb-1">暂无数据，请稍等数据加载...</p>
                  <small class="text-muted">数据加载完成后将自动显示图表</small>
                </div>
                <div v-else ref="chartRef" class="chart"></div>
              </div>
            </div>
          </div>

          <!-- 图例和统计信息 -->
          <div v-if="hasData && !loading" class="row mt-4">
            <div class="col-12">
              <div class="legend-container">
                <div class="legend-item">
                  <span class="legend-color" style="background-color: #5470c6;"></span>
                  <span class="legend-text">历史数据 (History)</span>
                </div>
                <div class="legend-item">
                  <span class="legend-color" style="background-color: #91cc75;"></span>
                  <span class="legend-text">真实数据 (Truth)</span>
                </div>
                <div v-if="showPrediction && predictionData.length > 0" class="legend-item">
                  <span class="legend-color" style="background-color: #ee6666;"></span>
                  <span class="legend-text">预测数据 (Prediction)</span>
                </div>
                <div v-if="predictionData.length > 0" class="legend-item ms-auto">
                  <div class="legend-stats">
                    <span>数据集: {{ selectedDataset }}</span>
                    <span class="mx-2">|</span>
                    <span>维度: {{ selectedDimension + 1 }}</span>
                    <span class="mx-2">|</span>
                    <span>RMSE: {{ rmse.toFixed(6) }}</span>
                    <span class="mx-2">|</span>
                    <span>MAE: {{ mae.toFixed(6) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 数据加载失败提示 -->
          <div v-if="loadError" class="row mt-4">
            <div class="col-12">
              <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                {{ loadError }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 全局加载状态 -->
      <div v-if="loading" class="loading-overlay">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">加载中...</span>
        </div>
        <p class="mt-2">正在处理数据...</p>
      </div>
    </div>
  </ContentComponent>
</template>

<script>
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from 'vue'
import ContentComponent from '@/components/ContentComponent.vue'
import * as echarts from 'echarts'
import $ from 'jquery'
import { BackendRootURL } from '@/config/config'
import { useStore } from 'vuex'

export default {
  name: 'ForcastTaskView',
  components: {
    ContentComponent,
  },
  setup() {
    const chartRef = ref(null)
    let chartInstance = null
    const store = useStore()
    
    // 响应式数据
    const loading = ref(false)
    const selectedDataset = ref('ETTh1')  // 默认数据集
    const selectedDimension = ref(0)
    const showPrediction = ref(false)
    const historyData = ref([])  // 形状: (length, dim)
    const truthData = ref([])    // 形状: (length, dim)
    const predictionData = ref([]) // 形状: (length, dim)
    const dimensions = ref([])   // 维度列表 [0, 1, 2, ...]
    const loadError = ref(null)
    const dataLoaded = ref(false)  // 新增：标记数据是否已加载
    
    // 可用的数据集列表
    const datasets = ref(['ETTh1', 'ETTh2', 'ETTm1', 'ETTm2'])
    
    // 计算属性
    const hasData = computed(() => {
      return historyData.value.length > 0 && truthData.value.length > 0 && dataLoaded.value
    })
    
    const rmse = computed(() => {
      if (predictionData.value.length === 0 || truthData.value.length === 0) return 0
      
      const predDim = selectedDimension.value
      const truthDim = Math.min(predDim, truthData.value[0].length - 1)
      
      let sum = 0
      const n = Math.min(predictionData.value.length, truthData.value.length)
      
      for (let i = 0; i < n; i++) {
        const predVal = predictionData.value[i][predDim] || 0
        const truthVal = truthData.value[i][truthDim] || 0
        sum += Math.pow(predVal - truthVal, 2)
      }
      
      return Math.sqrt(sum / n)
    })
    
    const mae = computed(() => {
      if (predictionData.value.length === 0 || truthData.value.length === 0) return 0
      
      const predDim = selectedDimension.value
      const truthDim = Math.min(predDim, truthData.value[0].length - 1)
      
      let sum = 0
      const n = Math.min(predictionData.value.length, truthData.value.length)
      
      for (let i = 0; i < n; i++) {
        const predVal = predictionData.value[i][predDim] || 0
        const truthVal = truthData.value[i][truthDim] || 0
        sum += Math.abs(predVal - truthVal)
      }
      
      return sum / n
    })
    
    // 数据统计信息
    const dataStats = computed(() => {
      if (!hasData.value) return []
      
      const getStats = (data, dim) => {
        if (data.length === 0) return { min: 0, max: 0, mean: 0, length: 0 }
        
        const values = data.map(row => row[dim] || 0)
        return {
          min: Math.min(...values),
          max: Math.max(...values),
          mean: values.reduce((a, b) => a + b, 0) / values.length,
          length: values.length
        }
      }
      
      const histStats = getStats(historyData.value, selectedDimension.value)
      const truthStats = getStats(truthData.value, selectedDimension.value)
      
      return [
        {
          id: 1,
          title: '历史数据长度',
          value: histStats.length.toLocaleString(),
          unit: '行',
          icon: 'fas fa-history',
          color: '#5470c6',
          description: '历史数据行数'
        },
        {
          id: 2,
          title: '真实数据长度',
          value: truthStats.length.toLocaleString(),
          unit: '行',
          icon: 'fas fa-chart-line',
          color: '#91cc75',
          description: '真实数据行数'
        },
        {
          id: 3,
          title: '数据范围',
          value: `${histStats.min.toFixed(4)} ~ ${histStats.max.toFixed(4)}`,
          unit: '',
          icon: 'fas fa-expand-alt',
          color: '#fac858',
          description: '历史数据最小/最大值'
        },
        {
          id: 4,
          title: '平均值',
          value: histStats.mean.toFixed(4),
          unit: '',
          icon: 'fas fa-calculator',
          color: '#ee6666',
          description: '历史数据平均值'
        }
      ]
    })
    
    // 防抖函数，避免频繁请求
    const debounce = (func, delay) => {
      let timeoutId
      return (...args) => {
        clearTimeout(timeoutId)
        timeoutId = setTimeout(() => {
          func.apply(this, args)
        }, delay)
      }
    }
    
    // 获取历史数据和真实数据
    const fetchData = async () => {
      return new Promise((resolve, reject) => {
        $.ajax({
          url: BackendRootURL + "/api/get_prediction_data",
          type: "POST",
          headers: {
            'Authorization': "Bearer " + store.state.user.token,
          },
          contentType: "application/json",
          data: JSON.stringify({
            dataname: selectedDataset.value,
            datatype: 1,
          }),
          success: (resp) => {
            if (resp.status === 0) {
              // 假设返回的数据结构
              historyData.value = resp.history_data || []
              truthData.value = resp.truth_data || []
              
              // 初始化维度列表
              if (historyData.value.length > 0 && historyData.value[0].length) {
                dimensions.value = Array.from({length: historyData.value[0].length}, (_, i) => i)
                selectedDimension.value = 0
              }
              
              console.log(`数据集 ${selectedDataset.value} 获取成功:`, {
                historyLength: historyData.value.length,
                truthLength: truthData.value.length,
                dimensions: dimensions.value
              })
              
              dataLoaded.value = true
              resolve(true)
            } else {
              console.error('获取数据失败:', resp.message)
              loadError.value = resp.message || '获取数据失败'
              dataLoaded.value = false
              reject(new Error(resp.message))
            }
          },
          error: (xhr, status, error) => {
            console.error('获取数据失败:', error)
            loadError.value = '获取数据失败，请检查网络连接'
            dataLoaded.value = false
            reject(error)
          }
        })
      })
    }
    
    // 防抖后的加载数据函数
    const debouncedFetchData = debounce(async () => {
      loading.value = true
      loadError.value = null
      dataLoaded.value = false
      
      try {
        await fetchData()
        
        // 数据加载成功后，等待DOM更新，然后初始化图表
        await nextTick()
        initChart()
      } catch (error) {
        console.error('数据加载失败:', error)
      } finally {
        loading.value = false
      }
    }, 300)
    
    // 数据集变化处理
    const handleDatasetChange = () => {
      console.log('数据集变化:', selectedDataset.value)
      
      // 重置数据和图表
      resetData()
      debouncedFetchData()
    }
    
    // 重置数据
    const resetData = () => {
      historyData.value = []
      truthData.value = []
      predictionData.value = []
      dimensions.value = []
      selectedDimension.value = 0
      showPrediction.value = false
      loadError.value = null
      dataLoaded.value = false
      
      if (chartInstance) {
        chartInstance.dispose()
        chartInstance = null
      }
    }
    
    // 获取预测数据
    const fetchPrediction = async () => {
      return new Promise((resolve, reject) => {
        $.ajax({
          url: BackendRootURL + "/api/predict",
          type: "POST",
          headers: {
            'Authorization': "Bearer " + store.state.user.token,
          },
          contentType: "application/json",
          data: JSON.stringify({
            dataname: selectedDataset.value,
            step: 96,
          }),
          success: (resp) => {
            if (resp.status === 0) {
              predictionData.value = resp.data || []
              loadError.value = null
              console.log(`数据集 ${selectedDataset.value} 预测数据获取成功:`, {
                predictionLength: predictionData.value.length
              })
              resolve(true)
            } else {
              console.error('获取预测数据失败:', resp.message)
              loadError.value = resp.message || '获取预测数据失败'
              reject(new Error(resp.message))
            }
          },
          error: (xhr, status, error) => {
            console.error('获取预测数据失败:', error)
            loadError.value = '获取预测数据失败，请检查网络连接'
            reject(error)
          }
        })
      })
    }
    
    // 初始化图表
    const initChart = () => {
      if (!chartRef.value) {
        console.error('图表容器未找到')
        return
      }
      
      if (chartInstance) {
        chartInstance.dispose()
        chartInstance = null
      }
      
      chartInstance = echarts.init(chartRef.value)
      updateChart()
    }
    
    // 更新图表
    const updateChart = () => {
      if (!chartInstance || !hasData.value) {
        console.log('无法更新图表:', {
          hasChartInstance: !!chartInstance,
          hasData: hasData.value,
          dataLoaded: dataLoaded.value
        })
        return
      }
      
      const dim = selectedDimension.value
      
      // 准备数据
      const historySeries = []
      const truthSeries = []
      const predictionSeries = []
      
      // 历史数据（蓝色）
      historyData.value.forEach((row, index) => {
        if (dim < row.length) {
          historySeries.push([index, row[dim]])
        }
      })
      
      // 真实数据（绿色） - 从历史数据结束后开始
      const historyLength = historyData.value.length
      truthData.value.forEach((row, index) => {
        if (dim < row.length) {
          truthSeries.push([historyLength + index, row[dim]])
        }
      })
      
      // 预测数据（红色） - 与真实数据对齐
      if (showPrediction.value && predictionData.value.length > 0) {
        predictionData.value.forEach((row, index) => {
          if (dim < row.length) {
            predictionSeries.push([historyLength + index, row[dim]])
          }
        })
      }
      
      // 图表配置
      const series = [
        {
          name: '历史数据',
          type: 'line',
          smooth: true,
          symbol: 'none',
          lineStyle: {
            width: 2
          },
          itemStyle: {
            color: '#5470c6'
          },
          data: historySeries
        },
        {
          name: '真实数据',
          type: 'line',
          smooth: true,
          symbol: 'none',
          lineStyle: {
            width: 1.5
          },
          itemStyle: {
            color: '#91cc75'
          },
          data: truthSeries
        }
      ]
      
      // 如果需要显示预测数据，添加到系列中
      if (showPrediction.value && predictionData.value.length > 0) {
        series.push({
          name: '预测数据',
          type: 'line',
          smooth: true,
          symbol: 'none',
          lineStyle: {
            width: 1.5
          },
          itemStyle: {
            color: '#ee6666'
          },
          data: predictionSeries
        })
      }
      
      const option = {
        title: {
          text: `时序预测 - ${selectedDataset.value} (维度 ${dim + 1})`,
          left: 'center',
          textStyle: {
            color: '#333',
            fontSize: 16
          }
        },
        tooltip: {
          trigger: 'axis',
          formatter: (params) => {
            const index = params[0].dataIndex
            let result = `时间点: ${index}<br/>`
            params.forEach(param => {
              result += `${param.seriesName}: ${param.value[1].toFixed(6)}<br/>`
            })
            return result
          }
        },
        legend: {
          data: series.map(s => s.name),
          bottom: 0,
          type: 'scroll'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: series.length > 1 ? '50px' : '3%',
          containLabel: true
        },
        xAxis: {
          type: 'value',
          name: '时间点',
          nameLocation: 'middle',
          nameGap: 25,
          axisLine: {
            lineStyle: {
              color: '#999'
            }
          },
          axisLabel: {
            formatter: (value) => {
              if (value >= 1000) {
                return (value / 1000).toFixed(0) + 'k'
              }
              return value
            }
          }
        },
        yAxis: {
          type: 'value',
          name: '数值',
          axisLine: {
            lineStyle: {
              color: '#999'
            }
          },
          splitLine: {
            lineStyle: {
              type: 'dashed',
              color: '#e0e0e0'
            }
          }
        },
        dataZoom: [
          {
            type: 'inside',
            start: 0,
            end: 100
          },
          {
            show: true,
            type: 'slider',
            bottom: series.length > 1 ? '20px' : '10px',
            start: 0,
            end: 100,
            height: 20
          }
        ],
        series: series
      }
      
      try {
        chartInstance.setOption(option, true)
        console.log('图表更新成功')
      } catch (error) {
        console.error('图表更新失败:', error)
      }
    }
    
    // 预测数据
    const predictData = async () => {
      loading.value = true
      loadError.value = null
      try {
        await fetchPrediction()
        showPrediction.value = true
        
        // 等待数据更新后再更新图表
        await nextTick()
        updateChart()
      } catch (error) {
        console.error('预测失败:', error)
      } finally {
        loading.value = false
      }
    }
    
    // 窗口大小变化处理
    const handleResize = () => {
      if (chartInstance) {
        chartInstance.resize()
      }
    }
    
    // 页面加载时自动加载数据
    const autoLoadData = async () => {
      console.log('开始自动加载默认数据...')
      console.log('已选择的数据集:', selectedDataset.value)
      
      try {
        loading.value = true
        await fetchData()
        
        // 等待DOM更新
        await nextTick()
        
        // 初始化图表
        initChart()
        
        // 添加窗口大小变化监听
        window.addEventListener('resize', handleResize)
        
        console.log('页面初始化完成')
      } catch (error) {
        console.error('初始化失败:', error)
      } finally {
        loading.value = false
      }
    }
    
    // 生命周期
    onMounted(async () => {
      await autoLoadData()
    })
    
    onUnmounted(() => {
      if (chartInstance) {
        chartInstance.dispose()
        chartInstance = null
      }
      window.removeEventListener('resize', handleResize)
    })
    
    // 监听维度变化
    watch(selectedDimension, () => {
      if (hasData.value) {
        updateChart()
      }
    })
    
    // 监听预测数据显示状态
    watch(showPrediction, () => {
      if (hasData.value) {
        updateChart()
      }
    })
    
    // 监听数据加载状态
    watch(dataLoaded, (newValue) => {
      console.log('数据加载状态变化:', newValue)
      if (newValue && chartInstance) {
        updateChart()
      }
    })
    
    return {
      chartRef,
      loading,
      selectedDataset,
      selectedDimension,
      showPrediction,
      historyData,
      truthData,
      predictionData,
      dimensions,
      datasets,
      hasData,
      rmse,
      mae,
      dataStats,
      loadError,
      handleDatasetChange,
      predictData
    }
  }
}
</script>

<style scoped>
.task-container {
  padding: 20px;
  position: relative;
}

.card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.card-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px 12px 0 0;
  padding: 20px;
}

.card-body {
  padding: 24px;
}

.control-panel {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e9ecef;
}

.input-group-text {
  background-color: #fff;
  border-right: none;
  font-weight: 500;
  min-width: 60px;
  justify-content: center;
}

.form-select {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 10px 16px;
  transition: all 0.3s;
  cursor: pointer;
}

.form-select:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}

.form-check-input:checked {
  background-color: #667eea;
  border-color: #667eea;
}

.form-check-label {
  cursor: pointer;
  user-select: none;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  padding: 10px 24px;
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.3s;
  width: 100%;
  cursor: pointer;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  background: #ccc;
  transform: none;
  box-shadow: none;
  cursor: not-allowed;
}

/* 统计卡片样式 */
.stat-card {
  background: #fff;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  height: 100%;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
}

.stat-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.stat-icon i {
  font-size: 18px;
}

.stat-title {
  font-size: 14px;
  color: #666;
  font-weight: 500;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.stat-content {
  display: flex;
  align-items: baseline;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #333;
  line-height: 1;
  font-family: 'Segoe UI', 'Arial', sans-serif;
}

.stat-unit {
  font-size: 14px;
  color: #999;
  margin-left: 6px;
  font-weight: 400;
}

.stat-desc {
  font-size: 12px;
  color: #999;
  line-height: 1.4;
  opacity: 0.8;
}

/* 图表容器 */
.chart-container {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  margin-top: 20px;
  min-height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart {
  height: 500px;
  width: 100%;
  min-height: 400px;
}

/* 无数据提示 */
.no-data {
  text-align: center;
  color: #6c757d;
  padding: 40px 20px;
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  width: 100%;
}

.no-data i {
  opacity: 0.5;
}

/* 图例 */
.legend-container {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 20px;
  padding: 12px 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-color {
  width: 20px;
  height: 4px;
  border-radius: 2px;
  flex-shrink: 0;
}

.legend-text {
  font-size: 14px;
  color: #333;
  font-weight: 500;
  white-space: nowrap;
}

.legend-stats {
  font-size: 14px;
  color: #666;
  background: white;
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.legend-stats span {
  white-space: nowrap;
}

/* 加载提示 */
.alert-info {
  background-color: #e7f3ff;
  border-color: #b6d4fe;
  color: #084298;
  border-radius: 8px;
}

/* 错误提示 */
.alert-danger {
  background-color: #f8d7da;
  border-color: #f5c6cb;
  color: #721c24;
  border-radius: 8px;
}

/* 全局加载状态 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .control-panel .row > div {
    margin-bottom: 15px;
  }
  
  .chart-container {
    min-height: 400px;
    padding: 10px;
  }
  
  .chart {
    height: 350px;
  }
  
  .legend-container {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .legend-item.ms-auto {
    margin-left: 0 !important;
    width: 100%;
  }
  
  .legend-stats {
    width: 100%;
    justify-content: center;
    text-align: center;
  }
  
  .legend-stats span {
    font-size: 12px;
  }
  
  .stat-card {
    padding: 15px;
  }
  
  .stat-value {
    font-size: 20px;
  }
}

@media (max-width: 576px) {
  .control-panel .row > div {
    margin-bottom: 10px;
  }
  
  .input-group-text {
    min-width: 50px;
    font-size: 14px;
  }
  
  .form-select {
    padding: 8px 12px;
    font-size: 14px;
  }
  
  .btn-primary {
    padding: 8px 16px;
    font-size: 14px;
  }
  
  .chart {
    height: 300px;
  }
}
</style>