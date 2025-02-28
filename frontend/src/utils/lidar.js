// frontend/src/utils/lidar.js
export const processLiDARData = (data) => {
  // Process LiDAR data here
  // This is a placeholder function. Replace it with actual data processing logic.
  return data.map(point => ({
    x: point.x,
    y: point.y,
    z: point.z,
    intensity: point.intensity,
  }));
};