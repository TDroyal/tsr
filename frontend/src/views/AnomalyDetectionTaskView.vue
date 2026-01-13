<template>
  <ContentComponent>
    <div class="task-container">
      <div class="card">
        <div class="card-header">
          <h5 class="mb-0">异常检测任务</h5>
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
              <div class="col-md-2">
                <div class="form-check form-switch">
                  <input class="form-check-input" type="checkbox" v-model="showOriginData" 
                         @change="updateChart" id="showOriginData">
                  <label class="form-check-label" for="showOriginData">
                    原始数据
                  </label>
                </div>
              </div>
              <div class="col-md-2">
                <div class="form-check form-switch">
                  <input class="form-check-input" type="checkbox" v-model="showAnomalyRegion" 
                         @change="updateChart" id="showAnomalyRegion">
                  <label class="form-check-label" for="showAnomalyRegion">
                    异常区域
                  </label>
                </div>
              </div>
              <div class="col-md-2">
                <button class="btn btn-primary" @click="detectAnomaly" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  {{ loading ? '检测中...' : '开始检测' }}
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
          <div v-if="originData.length > 0 && !loading" class="row mb-4">
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
                  <p class="mb-1">暂无数据，请点击"开始检测"按钮</p>
                  <small class="text-muted">点击后将获取原始数据并执行异常检测</small>
                </div>
                <div v-else ref="chartRef" class="chart"></div>
              </div>
            </div>
          </div>

          <!-- 检测结果统计 -->
          <div v-if="showDetectionResult && detectionResult.length > 0" class="row mt-4">
            <div class="col-12">
              <div class="detection-stats">
                <div class="row">
                  <div class="col-md-4">
                    <div class="stat-item">
                      <span class="stat-label">异常阈值</span>
                      <span class="stat-value">{{ threshold.toFixed(6) }}</span>
                    </div>
                  </div>
                  <div class="col-md-4">
                    <div class="stat-item">
                      <span class="stat-label">异常点数量</span>
                      <span class="stat-value">{{ anomalyCount }}</span>
                    </div>
                  </div>
                  <div class="col-md-4">
                    <div class="stat-item">
                      <span class="stat-label">异常比例</span>
                      <span class="stat-value">{{ anomalyRatio.toFixed(2) }}%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 图例和统计信息 -->
          <div v-if="hasData && !loading" class="row mt-4">
            <div class="col-12">
              <div class="legend-container">
                <div v-if="showOriginData" class="legend-item">
                  <span class="legend-color" style="background-color: #5470c6;"></span>
                  <span class="legend-text">原始数据 (Origin)</span>
                </div>
                <div v-if="showDetectionResult && reconstructionData.length > 0" class="legend-item">
                  <span class="legend-color" style="background-color: #ee6666;"></span>
                  <span class="legend-text">重构数据 (Reconstruction)</span>
                </div>
                <div v-if="showDetectionResult && anomalyScore.length > 0" class="legend-item">
                  <span class="legend-color" style="background-color: #91cc75;"></span>
                  <span class="legend-text">异常分数 (Anomaly Score)</span>
                </div>
                <div v-if="showAnomalyRegion && showDetectionResult && predLabels.length > 0" class="legend-item">
                  <span class="legend-color" style="background-color: rgba(255, 0, 0, 0.1);"></span>
                  <span class="legend-text">异常区域 (Region)</span>
                </div>
                <div v-if="showDetectionResult" class="legend-item ms-auto">
                  <div class="legend-stats">
                    <span>数据集: {{ selectedDataset }}</span>
                    <span class="mx-2">|</span>
                    <span>维度: {{ selectedDimension + 1 }}</span>
                    <span class="mx-2">|</span>
                    <span>阈值: {{ threshold.toFixed(6) }}</span>
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
  name: 'AnomalyDetectionTaskView',
  components: {
    ContentComponent,
  },
  setup() {
    const chartRef = ref(null)
    let chartInstance = null
    const store = useStore()
    
    // 响应式数据
    const loading = ref(false)
    const selectedDataset = ref('SMD')  // 默认数据集
    const selectedDimension = ref(0)
    const showOriginData = ref(true)  // 控制原始数据显示
    const showDetectionResult = ref(false)  // 控制检测结果显示
    const showAnomalyRegion = ref(true)  // 控制异常区域显示
    const originData = ref([])  // 原始数据
    const reconstructionData = ref([])  // 重构数据
    const anomalyScore = ref([])  // 异常分数
    const predLabels = ref([])  // 预测标签
    const threshold = ref(0)  // 异常阈值
    const dimensions = ref([])  // 维度列表
    const loadError = ref(null)
    const dataLoaded = ref(false)
    
    // 可用的数据集列表
    const datasets = ref(['SMD', 'PSM', 'MSL'])
    
    // 计算属性
    const hasData = computed(() => {
      return originData.value.length > 0 && dataLoaded.value
    })
    
    const detectionResult = computed(() => {
      return predLabels.value
    })
    
    const anomalyCount = computed(() => {
      if (predLabels.value.length === 0) return 0
      return predLabels.value.filter(label => label === 1).length
    })
    
    const anomalyRatio = computed(() => {
      if (predLabels.value.length === 0) return 0
      return (anomalyCount.value / predLabels.value.length) * 100
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
      
      const originStats = getStats(originData.value, selectedDimension.value)
      const reconstructionStats = getStats(reconstructionData.value, selectedDimension.value)
      
      return [
        {
          id: 1,
          title: '数据长度',
          value: originStats.length.toLocaleString(),
          unit: '行',
          icon: 'fas fa-ruler-horizontal',
          color: '#5470c6',
          description: '原始数据行数'
        },
        {
          id: 2,
          title: '数据范围',
          value: `${originStats.min.toFixed(4)} ~ ${originStats.max.toFixed(4)}`,
          unit: '',
          icon: 'fas fa-expand-alt',
          color: '#91cc75',
          description: '原始数据最小/最大值'
        },
        {
          id: 3,
          title: '平均值',
          value: originStats.mean.toFixed(4),
          unit: '',
          icon: 'fas fa-calculator',
          color: '#ee6666',
          description: '原始数据平均值'
        },
        {
          id: 4,
          title: '重构误差',
          value: reconstructionStats.length > 0 
            ? Math.abs(originStats.mean - reconstructionStats.mean).toFixed(4) 
            : '0.0000',
          unit: '',
          icon: 'fas fa-bullseye',
          color: '#fac858',
          description: '原始与重构数据平均差异'
        }
      ]
    })
    
    // 防抖函数
    const debounce = (func, delay) => {
      let timeoutId
      return (...args) => {
        clearTimeout(timeoutId)
        timeoutId = setTimeout(() => {
          func.apply(this, args)
        }, delay)
      }
    }
    
    // 获取原始数据
    const fetchOriginData = async () => {
      return new Promise((resolve, reject) => {
        $.ajax({
          url: BackendRootURL + "/api/get_anomalydetection_data",
          type: "POST",
          headers: {
            'Authorization': "Bearer " + store.state.user.token,
          },
          contentType: "application/json",
          data: JSON.stringify({
            dataname: selectedDataset.value,
          }),
          success: (resp) => {
            if (resp.status === 0) {
              originData.value = resp.origin_data || []
              
              // 初始化维度列表（限制最多显示5个维度）
              if (originData.value.length > 0 && originData.value[0].length) {
                const maxDims = Math.min(originData.value[0].length, 5)
                dimensions.value = Array.from({length: maxDims}, (_, i) => i)
                selectedDimension.value = 0
              }
              
              console.log(`数据集 ${selectedDataset.value} 原始数据获取成功:`, {
                dataLength: originData.value.length,
                dimensions: dimensions.value
              })
              
              dataLoaded.value = true
              resolve(true)
            } else {
              console.error('获取原始数据失败:', resp.message)
              loadError.value = resp.message || '获取原始数据失败'
              dataLoaded.value = false
              reject(new Error(resp.message))
            }
          },
          error: (xhr, status, error) => {
            console.error('获取原始数据失败:', error)
            loadError.value = '获取原始数据失败，请检查网络连接'
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
        await fetchOriginData()
        
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
      
      // 重置数据
      resetData()
      debouncedFetchData()
    }
    
    // 重置数据
    const resetData = () => {
      originData.value = []
      reconstructionData.value = []
      anomalyScore.value = []
      predLabels.value = []
      threshold.value = 0
      dimensions.value = []
      selectedDimension.value = 0
      showDetectionResult.value = false
      loadError.value = null
      dataLoaded.value = false
      
      if (chartInstance) {
        chartInstance.dispose()
        chartInstance = null
      }
    }
    
    // 执行异常检测
    const detectAnomaly = async () => {
      loading.value = true
      loadError.value = null
      
      try {
        // 获取检测结果
        const response = await new Promise((resolve, reject) => {
          $.ajax({
            url: BackendRootURL + "/api/anomalydetection",
            type: "POST",
            headers: {
              'Authorization': "Bearer " + store.state.user.token,
            },
            contentType: "application/json",
            data: JSON.stringify({
              dataname: selectedDataset.value,
            }),
            success: (resp) => {
              if (resp.status === 0) {
                resolve(resp)
              } else {
                reject(new Error(resp.message))
              }
            },
            error: (xhr, status, error) => {
              reject(error)
            }
          })
        })
        
        // 更新检测结果数据
        threshold.value = response.threshold || 0
        reconstructionData.value = response.reconstruction_data || []
        anomalyScore.value = response.anomaly_score || []
        predLabels.value = response.pred_labels || []
        
        showDetectionResult.value = true
        
        console.log('异常检测完成:', {
          threshold: threshold.value,
          reconstructionLength: reconstructionData.value.length,
          anomalyScoreLength: anomalyScore.value.length,
          predLabelsLength: predLabels.value.length,
          anomalyCount: anomalyCount.value
        })
        
        // 更新图表
        await nextTick()
        updateChart()
        
      } catch (error) {
        console.error('异常检测失败:', error)
        loadError.value = '异常检测失败，请检查网络连接'
      } finally {
        loading.value = false
      }
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
      
      // 准备数据系列
      const series = []
      
      // 异常区域系列（作为一个独立的系列）
      if (showAnomalyRegion.value && showDetectionResult.value && predLabels.value.length > 0) {
        const anomalyRegions = []
        let regionStart = null
        
        // 找出所有连续的异常区域
        for (let i = 0; i < predLabels.value.length; i++) {
          if (predLabels.value[i] === 1) {
            if (regionStart === null) {
              regionStart = i
            }
          } else {
            if (regionStart !== null) {
              anomalyRegions.push({
                xStart: regionStart,
                xEnd: i - 1
              })
              regionStart = null
            }
          }
        }
        
        // 处理最后一个异常区域
        if (regionStart !== null) {
          anomalyRegions.push({
            xStart: regionStart,
            xEnd: predLabels.value.length - 1
          })
        }
        
        // 创建独立的数据系列用于异常区域
        if (anomalyRegions.length > 0) {
          // 为每个区域创建数据点
          const anomalyRegionData = []
          
          anomalyRegions.forEach(region => {
            // 添加区域开始和结束的数据点
            anomalyRegionData.push({
              value: [region.xStart, 0],
              itemStyle: {
                color: 'transparent'
              }
            })
            
            // 计算区域的中间点用于显示
            const midX = (region.xStart + region.xEnd) / 2
            anomalyRegionData.push({
              value: [midX, 0],
              itemStyle: {
                color: 'transparent'
              }
            })
            
            anomalyRegionData.push({
              value: [region.xEnd, 0],
              itemStyle: {
                color: 'transparent'
              }
            })
          })
          
          series.push({
            name: '异常区域',
            type: 'line',
            data: anomalyRegionData,
            markArea: {
              silent: true,
              itemStyle: {
                color: 'rgba(255, 0, 0, 0.1)',
                borderWidth: 0
              },
              data: anomalyRegions.map(region => [
                {
                  xAxis: region.xStart,
                  itemStyle: {
                    color: 'rgba(255, 0, 0, 0.1)',
                    borderWidth: 0
                  }
                },
                {
                  xAxis: region.xEnd
                }
              ])
            },
            lineStyle: {
              opacity: 0
            },
            z: 0  // 确保在最底层
          })
        }
      }
      
      // 原始数据系列
      if (showOriginData.value) {
        const originSeriesData = originData.value.map((row, index) => {
          return [index, row[dim] || 0]
        })
        
        series.push({
          name: '原始数据',
          type: 'line',
          smooth: true,
          symbol: 'none',
          lineStyle: {
            width: 2
          },
          itemStyle: {
            color: '#5470c6'
          },
          data: originSeriesData,
          z: 1  // 在异常区域上方
        })
      }
      
      // 重构数据系列（如果显示检测结果）- 使用红色 (#ee6666)
      if (showDetectionResult.value && reconstructionData.value.length > 0) {
        const reconstructionSeriesData = reconstructionData.value.map((row, index) => {
          return [index, row[dim] || 0]
        })
        
        series.push({
          name: '重构数据',
          type: 'line',
          smooth: true,
          symbol: 'none',
          lineStyle: {
            width: 1.5
          },
          itemStyle: {
            color: '#ee6666'
          },
          data: reconstructionSeriesData,
          z: 2
        })
      }
      
      // 异常分数系列（如果显示检测结果）- 使用绿色 (#91cc75)
      if (showDetectionResult.value && anomalyScore.value.length > 0) {
        const anomalySeriesData = anomalyScore.value.map((row, index) => {
          return [index, row[dim] || 0]
        })
        
        series.push({
          name: '异常分数',
          type: 'line',
          yAxisIndex: 1, // 使用第二个Y轴
          smooth: true,
          symbol: 'none',
          lineStyle: {
            width: 1.5
          },
          itemStyle: {
            color: '#91cc75'
          },
          data: anomalySeriesData,
          z: 3
        })
      }
      
      // 阈值线
      if (showDetectionResult.value) {
        series.push({
          name: '异常阈值',
          type: 'line',
          yAxisIndex: 1,
          lineStyle: {
            type: 'dashed',
            width: 1,
            color: '#ff0000'
          },
          markLine: {
            silent: true,
            data: [{
              yAxis: threshold.value,
              name: '阈值',
              lineStyle: {
                type: 'dashed',
                color: '#ff0000'
              },
              label: {
                formatter: '阈值: {c}',
                position: 'end'
              }
            }]
          },
          data: [],
          z: 4
        })
      }
      
      const option = {
        title: {
          text: `异常检测 - ${selectedDataset.value} (维度 ${dim + 1})`,
          left: 'center',
          textStyle: {
            color: '#333',
            fontSize: 16
          }
        },
        tooltip: {
          trigger: 'axis',
          formatter: (params) => {
            let result = `时间点: ${params[0].dataIndex}<br/>`
            params.forEach(param => {
              if (param.seriesName === '异常阈值') {
                result += `${param.seriesName}: ${threshold.value.toFixed(6)}<br/>`
              } else if (param.value && param.value.length === 2) {
                result += `${param.seriesName}: ${param.value[1].toFixed(6)}<br/>`
              } else if (param.seriesName) {
                result += `${param.seriesName}<br/>`
              }
            })
            return result
          }
        },
        legend: {
          data: series.map(s => s.name),
          bottom: 0,
          type: 'scroll',
          selected: {
            '异常区域': showAnomalyRegion.value
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: series.length > 1 ? '50px' : '3%',
          top: '10%',
          containLabel: true
        },
        xAxis: {
          type: 'value',
          name: '时间点',
          nameLocation: 'middle',
          nameGap: 25
        },
        yAxis: [
          {
            type: 'value',
            name: '数据值',
            position: 'left',
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
          {
            type: 'value',
            name: '异常分数',
            position: 'right',
            axisLine: {
              lineStyle: {
                color: '#91cc75'
              }
            },
            splitLine: {
              show: false
            }
          }
        ],
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
        console.log('图表更新成功', {
          原始数据: showOriginData.value,
          检测结果: showDetectionResult.value,
          异常区域: showAnomalyRegion.value
        })
      } catch (error) {
        console.error('图表更新失败:', error)
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
        await fetchOriginData()
        
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
    
    // 监听原始数据显示状态
    watch(showOriginData, () => {
      if (hasData.value) {
        updateChart()
      }
    })
    
    // 监听检测结果显示状态
    watch(showDetectionResult, () => {
      if (hasData.value) {
        updateChart()
      }
    })
    
    // 监听异常区域显示状态
    watch(showAnomalyRegion, () => {
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
      showOriginData,
      showDetectionResult,
      showAnomalyRegion,
      originData,
      reconstructionData,
      anomalyScore,
      predLabels,
      threshold,
      dimensions,
      datasets,
      hasData,
      detectionResult,
      anomalyCount,
      anomalyRatio,
      dataStats,
      loadError,
      handleDatasetChange,
      detectAnomaly
    }
  }
}
</script>

<style scoped>
/* 样式保持不变，同之前的代码 */
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
  font-size: 14px;
  white-space: nowrap;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  padding: 10px 16px;
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.3s;
  width: 100%;
  cursor: pointer;
  font-size: 14px;
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

/* 检测结果统计 */
.detection-stats {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e9ecef;
}

.stat-item {
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #333;
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
  
  .detection-stats .row > div {
    margin-bottom: 15px;
  }
  
  .form-check-label {
    font-size: 13px;
  }
  
  .btn-primary {
    font-size: 13px;
    padding: 8px 12px;
  }
}

@media (max-width: 576px) {
  .control-panel .row > div {
    margin-bottom: 10px;
  }
  
  .input-group-text {
    min-width: 50px;
    font-size: 13px;
  }
  
  .form-select {
    padding: 6px 10px;
    font-size: 13px;
  }
  
  .btn-primary {
    padding: 6px 10px;
    font-size: 13px;
  }
  
  .chart {
    height: 300px;
  }
  
  .stat-item .stat-value {
    font-size: 20px;
  }
  
  .form-check-label {
    font-size: 12px;
  }
}
</style>