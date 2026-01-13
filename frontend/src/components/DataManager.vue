<!-- src/components/DataManager.vue -->
<template>
  <div class="data-manager">
    <div class="card">
      <div class="card-header">
        <h5 class="mb-0">时序数据库</h5>
      </div>
      <div class="card-body">
        <!-- 数据集选择 -->
        <div class="row mb-4">
          <div class="col-md-6">
            <label class="form-label">选择数据集</label>
            <select v-model="selectedDataset" class="form-select" @change="handleSelectionChange">
              <option value="">请选择数据集</option>
              <option value="">时序预测数据集</option>
              <option v-for="dataset in forecastDatasets" :key="dataset.name" :value="dataset.name">
                {{ dataset.name }}
              </option>
              <option value="">时序异常检测数据集</option>
              <option v-for="dataset in anomalyDatasets" :key="dataset.name" :value="dataset.name" >
                {{ dataset.name }}
              </option>
            </select>
          </div>
          <div class="col-md-6">
            <label class="form-label">数据类型</label>
            <select v-model="selectedDataType" class="form-select" @change="handleSelectionChange">
              <option value="1">训练数据</option>
              <option value="2">测试数据</option>
              <option value="3" v-if="hasLabelDatasets.includes(selectedDataset)">标签数据</option>
            </select>
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
        <div v-if="currentData && !loading" class="row mb-4">
          <h6 class="mb-3">数据统计信息</h6>
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
        
        <!-- 数据图表 -->
        <div v-if="currentData && chartOption && !loading" class="row">
          <div class="col-12">
            <div class="chart-container">
              <div ref="chartRef" class="chart"></div>
            </div>
          </div>
        </div>
        
        <!-- 无数据提示 -->
        <div v-if="!loading && (!selectedDataset || !currentData)" class="row mt-4">
          <div class="col-12">
            <div class="alert alert-light text-center border">
              <i class="fas fa-database fa-2x text-muted mb-3"></i>
              <p class="mb-1">请选择数据集和数据类型</p>
              <small class="text-muted">选择后将自动加载数据</small>
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
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import $ from 'jquery'
import { BackendRootURL } from '@/config/config'
import {useStore} from 'vuex'

export default {
  name: 'DataManager',
  setup() {
    const store = useStore()
    const chartRef = ref(null)
    let chartInstance = null
    
    // 响应式数据 - 设置默认值
    const selectedDataset = ref('SMD')  // 默认选择SMD
    const selectedDataType = ref('1')   // 默认选择训练数据
    const datasets = ref([])
    const loading = ref(false)
    const currentData = ref(null)
    const dataInfo = ref(null)
    const loadError = ref(null)
    const hasLabelDatasets = ref(['SMD', 'PSM', 'MSL'])
    
    const forecastDatasets = computed(() => {
      return datasets.value.filter(dataset => 
        !hasLabelDatasets.value.includes(dataset.name)
      )
    })

    const anomalyDatasets = computed(() => {
      return datasets.value.filter(dataset => 
        hasLabelDatasets.value.includes(dataset.name)
      )
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
    
    // 计算统计信息卡片
    const dataStats = computed(() => {
      if (!currentData.value || !currentData.value.statistic) return []
      
      const stat = currentData.value.statistic
      return [
        {
          id: 1,
          title: '数据长度',
          value: stat.data_length.toLocaleString(),
          unit: '行',
          icon: 'fas fa-ruler-horizontal',
          color: '#5470c6',
          description: '总数据行数'
        },
        {
          id: 2,
          title: '数据维度',
          value: stat.data_dimension,
          unit: '维',
          icon: 'fas fa-layer-group',
          color: '#91cc75',
          description: '特征维度数量'
        },
        {
          id: 3,
          title: '数据范围',
          value: `${stat.data_min.toFixed(4)} ~ ${stat.data_max.toFixed(4)}`,
          unit: '',
          icon: 'fas fa-expand-alt',
          color: '#fac858',
          description: '最小/最大值'
        },
        {
          id: 4,
          title: '平均值',
          value: stat.data_mean.toFixed(4),
          unit: '',
          icon: 'fas fa-chart-line',
          color: '#ee6666',
          description: '数据平均值'
        }
      ]
    })
    
    // 计算图表配置
    const chartOption = computed(() => {
      if (!currentData.value || !currentData.value.sample_data || currentData.value.sample_data.length === 0) {
        return null
      }
      
      const sampleData = currentData.value.sample_data
      const dataName = dataInfo.value?.datatype_name || '数据'
      
      // 如果数据是多维的，显示每个维度的折线
      const dimensions = currentData.value.statistic.data_dimension
      const series = []
      
      if (dimensions === 1) {
        // 单维数据
        series.push({
          name: dataName,
          type: 'line',
          smooth: true,
          symbol: 'none',
          lineStyle: {
            width: 2
          },
          itemStyle: {
            color: '#5470c6'
          },
          data: sampleData.map((item, index) => [index, item[0]])
        })
      } else {
        // 多维数据，显示前5个维度
        const maxDimensions = Math.min(dimensions, 5)
        const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de']
        
        for (let i = 0; i < maxDimensions; i++) {
          series.push({
            name: `维度 ${i + 1}`,
            type: 'line',
            smooth: true,
            symbol: 'none',
            lineStyle: {
              width: 1.5
            },
            itemStyle: {
              color: colors[i % colors.length]
            },
            data: sampleData.map((item, index) => [index, item[i]])
          })
        }
      }
      
      return {
        title: {
          text: `${dataInfo.value?.dataname} - ${dataName} 可视化`,
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
          bottom: dimensions > 1 ? '50px' : '3%',
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
            bottom: dimensions > 1 ? '20px' : '10px',
            start: 0,
            end: 100,
            height: 20
          }
        ],
        series: series
      }
    })
    
    // 获取数据集列表
    const fetchDatasets = async () => {
      return new Promise((resolve) => {
        $.ajax({
          url: BackendRootURL + "/api/datasets",
          type: "GET",
          headers: {
            'Authorization': "Bearer " + store.state.user.token,
          },
          dataType: "json",
          success: (resp) => {
            if (resp.status === 0) {
              datasets.value = resp.datasets
              console.log('数据集列表加载成功:', datasets.value)
              resolve(true)
            } else {
              console.error('获取数据集列表失败:', resp.message)
              loadError.value = '获取数据集列表失败'
              resolve(false)
            }
          },
          error: (xhr, status, error) => {
            console.error('获取数据集列表失败:', error)
            loadError.value = '获取数据集列表失败，请检查网络连接'
            resolve(false)
          }
        })
      })
    }
    
    // 加载数据
    const loadData = async () => {
      if (!selectedDataset.value) {
        currentData.value = null
        dataInfo.value = null
        loadError.value = null
        return
      }
      
      loading.value = true
      loadError.value = null
      
      // 清除现有的图表实例
      if (chartInstance) {
        chartInstance.dispose()
        chartInstance = null
      }
      
      $.ajax({
        url: BackendRootURL + "/api/getdata",
        type: "POST",
        headers: {
          'Authorization': "Bearer " + store.state.user.token,
        },
        contentType: "application/json",
        data: JSON.stringify({
          dataname: selectedDataset.value,
          datatype: parseInt(selectedDataType.value)
        }),
        dataType: "json",
        success: (resp) => {
          loading.value = false
          
          if (resp.status === 0) {
            currentData.value = resp
            dataInfo.value = resp.data_info
            console.log('数据加载成功:', {
              dataLength: resp.statistic.data_length,
              dimensions: resp.statistic.data_dimension,
              sampleCount: resp.sample_data.length
            })
            
            // 立即初始化图表
            nextTick(() => {
              setTimeout(() => {
                initChart()
              }, 50)
            })
            
          } else {
            loadError.value = resp.message || '数据加载失败'
            currentData.value = null
            dataInfo.value = null
          }
        },
        error: (xhr, status, error) => {
          loading.value = false
          console.error('加载数据失败:', error)
          
          let errorMessage = "加载数据失败"
          if (xhr.responseJSON && xhr.responseJSON.message) {
            errorMessage = xhr.responseJSON.message
          } else if (xhr.responseText) {
            try {
              const errorData = JSON.parse(xhr.responseText)
              errorMessage = errorData.message || errorMessage
            } catch (e) {
              errorMessage = '服务器响应异常'
            }
          }
          
          loadError.value = errorMessage
          currentData.value = null
          dataInfo.value = null
        }
      })
    }
    
    // 防抖后的加载数据函数
    const debouncedLoadData = debounce(loadData, 300)
    
    // 选择框变化处理
    const handleSelectionChange = () => {
      console.log('选择框变化，触发数据加载')
      console.log('数据集:', selectedDataset.value)
      console.log('数据类型:', selectedDataType.value)
      debouncedLoadData()
    }
    
    // 初始化图表
    const initChart = () => {
      console.log('初始化图表...')
      
      if (!chartRef.value) {
        console.error('图表容器未找到')
        return
      }
      
      if (!chartOption.value) {
        console.error('图表配置未生成')
        return
      }
      
      try {
        // 销毁旧的图表实例
        if (chartInstance) {
          chartInstance.dispose()
        }
        
        // 初始化ECharts实例
        chartInstance = echarts.init(chartRef.value)
        
        // 设置图表选项
        chartInstance.setOption(chartOption.value)
        
        console.log('图表初始化成功')
        
      } catch (error) {
        console.error('图表初始化失败:', error)
      }
    }
    
    // 窗口大小变化处理
    const handleResize = () => {
      if (chartInstance) {
        chartInstance.resize()
      }
    }
    
    // 页面加载时自动加载SMD训练数据
    const autoLoadData = async () => {
      console.log('开始自动加载默认数据...')
      console.log('已选择的数据集:', selectedDataset.value)
      console.log('已选择的数据类型:', selectedDataType.value)
      
      // 先获取数据集列表
      await fetchDatasets()
      
      // 检查SMD是否在数据集中
      const hasSMD = datasets.value.some(dataset => dataset.name === 'SMD')
      if (!hasSMD) {
        console.warn('SMD不在可用数据集中')
        loadError.value = 'SMD数据集不可用'
        return
      }
      
      // 自动加载数据
      console.log('开始加载SMD训练数据...')
      await loadData()
    }
    
    // 监听选择框变化
    watch([selectedDataset, selectedDataType], () => {
      handleSelectionChange()
    })
    
    // 生命周期
    onMounted(async () => {
      // 添加窗口大小变化监听
      window.addEventListener('resize', handleResize)
      
      // 自动加载默认数据
      await autoLoadData()
    })
    
    onUnmounted(() => {
      if (chartInstance) {
        chartInstance.dispose()
        chartInstance = null
      }
      window.removeEventListener('resize', handleResize)
    })
    
    // 监听图表配置变化
    watch(chartOption, (newOption) => {
      console.log('图表配置发生变化')
      if (newOption && chartRef.value) {
        // 等待DOM更新完成
        nextTick(() => {
          setTimeout(() => {
            initChart()
          }, 50)
        })
      }
    })
    
    return {
      chartRef,
      selectedDataset,
      selectedDataType,
      datasets,
      loading,
      currentData,
      dataStats,
      chartOption,
      loadError,
      handleSelectionChange,
      hasLabelDatasets,
      forecastDatasets,
      anomalyDatasets,
    }
  }
}
</script>

<style scoped>
.data-manager {
  padding: 20px;
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

.form-label {
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
}

.form-select {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 10px 16px;
  transition: all 0.3s;
}

.form-select:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
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
}

.chart {
  height: 500px;
  width: 100%;
  min-height: 400px;
}

/* 加载提示 */
.alert-info {
  background-color: #e7f3ff;
  border-color: #b6d4fe;
  color: #084298;
}

/* 无数据提示 */
.alert-light {
  background-color: #f8f9fa;
  border-color: #e9ecef;
  color: #6c757d;
  padding: 40px 20px;
}

.alert-light i {
  opacity: 0.5;
}

/* 错误提示 */
.alert-danger {
  background-color: #f8d7da;
  border-color: #f5c6cb;
  color: #721c24;
}
</style>