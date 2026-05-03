import { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, Text, Html, Float, Sparkles } from '@react-three/drei'
import * as THREE from 'three'
import { getTopology, getCategories } from '../api.js'

const CATEGORY_COLORS = {
  'AI & Machine Learning': 0x00ff88,
  'Web Development': 0x4488ff,
  'Mobile Development': 0xff8844,
  'DevOps & Infrastructure': 0x88ff44,
  'Security': 0xff4488,
  'Data Science': 0x8844ff,
  'Database': 0xffff44,
  'Programming Languages': 0x44ffff,
  'Frameworks & Libraries': 0xff44ff,
  'Tools & Utilities': 0x888888,
  'Documentation': 0x44ff88,
  'Testing': 0xffaa44,
  'Game Development': 0x8844ff,
  'IoT': 0x44aaff,
  'Blockchain & Crypto': 0xffaa00,
  'Uncategorized': 0x666666,
}

const SOURCE_ICONS = {
  github: '🐙',
  hn: '📰',
  ph: '🚀',
}

function NodeSphere({ node, isSelected, onClick, isHovered, onHover }) {
  const meshRef = useRef()
  const [hovered, setHovered] = useState(false)
  const color = CATEGORY_COLORS[node.category] || 0x666666
  
  const scale = useMemo(() => {
    const base = 1 + node.size * 0.3
    return hovered || isSelected ? base * 1.3 : base
  }, [node.size, hovered, isSelected])

  const opacity = useMemo(() => {
    if (isSelected) return 1
    if (hovered) return 0.9
    return 0.7
  }, [isSelected, hovered])

  const handlePointerOver = (e) => {
    e.stopPropagation()
    setHovered(true)
    onHover && onHover(node)
  }

  const handlePointerOut = (e) => {
    e.stopPropagation()
    setHovered(false)
    onHover && onHover(null)
  }

  const handleClick = (e) => {
    e.stopPropagation()
    onClick && onClick(node)
  }

  return (
    <group position={[node.x, node.y, node.z]}>
      <mesh
        ref={meshRef}
        scale={[scale, scale, scale]}
        onPointerOver={handlePointerOver}
        onPointerOut={handlePointerOut}
        onClick={handleClick}
      >
        <sphereGeometry args={[1, 32, 32]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={isSelected ? 0.6 : 0.15}
          metalness={0.3}
          roughness={0.4}
          transparent
          opacity={opacity}
        />
      </mesh>
      
      {isSelected && (
        <mesh>
          <sphereGeometry args={[1.5, 32, 32]} />
          <meshBasicMaterial
            color={color}
            transparent
            opacity={0.15}
            side={THREE.BackSide}
          />
        </mesh>
      )}
    </group>
  )
}

function LinkLine({ source, target, strength }) {
  const points = useMemo(() => {
    return [
      new THREE.Vector3(source.x, source.y, source.z),
      new THREE.Vector3(target.x, target.y, target.z),
    ]
  }, [source, target])

  const lineGeometry = useMemo(() => {
    const geometry = new THREE.BufferGeometry().setFromPoints(points)
    return geometry
  }, [points])

  const opacity = 0.1 + strength * 0.4

  return (
    <line geometry={lineGeometry}>
      <lineBasicMaterial
        color={0x6366f1}
        transparent
        opacity={opacity}
      />
    </line>
  )
}

function NodeLabel({ node, isVisible }) {
  if (!isVisible) return null
  
  return (
    <group position={[node.x, node.y + 1.5, node.z]}>
      <Html center distanceFactor={100}>
        <div className="node-label">
          <div className="node-label-icon">{SOURCE_ICONS[node.source] || '📦'}</div>
          <div className="node-label-title">{node.title}</div>
          <div className="node-label-match">{Math.round(node.match_score * 100)}% match</div>
        </div>
      </Html>
    </group>
  )
}

function PhysicsSimulation({ nodes, links, onNodesUpdate }) {
  const nodesRef = useRef([...nodes])
  const velocitiesRef = useRef(nodes.map(() => ({ x: 0, y: 0, z: 0 })))
  const lastUpdateRef = useRef(0)

  useFrame((state, delta) => {
    const now = Date.now()
    if (now - lastUpdateRef.current < 16) return
    lastUpdateRef.current = now

    const currentNodes = nodesRef.current
    const velocities = velocitiesRef.current
    const k = 2
    const repulsion = 150
    const damping = 0.92
    const centerForce = 0.01

    const forces = currentNodes.map(() => ({ x: 0, y: 0, z: 0 }))

    for (let i = 0; i < currentNodes.length; i++) {
      for (let j = i + 1; j < currentNodes.length; j++) {
        const n1 = currentNodes[i]
        const n2 = currentNodes[j]
        
        const dx = n2.x - n1.x
        const dy = n2.y - n1.y
        const dz = n2.z - n1.z
        const distSq = dx * dx + dy * dy + dz * dz
        
        if (distSq < 1) continue
        
        const dist = Math.sqrt(distSq)
        const forceMag = repulsion / distSq
        
        const fx = (dx / dist) * forceMag
        const fy = (dy / dist) * forceMag
        const fz = (dz / dist) * forceMag
        
        forces[i].x -= fx
        forces[i].y -= fy
        forces[i].z -= fz
        forces[j].x += fx
        forces[j].y += fy
        forces[j].z += fz
      }
    }

    for (const link of links) {
      const sourceNode = currentNodes.find(n => n.id === link.source)
      const targetNode = currentNodes.find(n => n.id === link.target)
      
      if (!sourceNode || !targetNode) continue
      
      const sourceIdx = currentNodes.indexOf(sourceNode)
      const targetIdx = currentNodes.indexOf(targetNode)
      
      const dx = targetNode.x - sourceNode.x
      const dy = targetNode.y - sourceNode.y
      const dz = targetNode.z - sourceNode.z
      const dist = Math.sqrt(dx * dx + dy * dy + dz * dz)
      
      if (dist < 1) continue
      
      const targetDist = k * 5 * (1.5 - link.strength)
      const forceMag = (dist - targetDist) * 0.05 * link.strength
      
      const fx = (dx / dist) * forceMag
      const fy = (dy / dist) * forceMag
      const fz = (dz / dist) * forceMag
      
      forces[sourceIdx].x += fx
      forces[sourceIdx].y += fy
      forces[sourceIdx].z += fz
      forces[targetIdx].x -= fx
      forces[targetIdx].y -= fy
      forces[targetIdx].z -= fz
    }

    let hasChanges = false
    for (let i = 0; i < currentNodes.length; i++) {
      const node = currentNodes[i]
      const vel = velocities[i]
      const force = forces[i]
      
      force.x -= node.x * centerForce
      force.y -= node.y * centerForce
      force.z -= node.z * centerForce
      
      vel.x = (vel.x + force.x) * damping
      vel.y = (vel.y + force.y) * damping
      vel.z = (vel.z + force.z) * damping
      
      const speed = Math.sqrt(vel.x * vel.x + vel.y * vel.y + vel.z * vel.z)
      if (speed > 2) {
        vel.x = (vel.x / speed) * 2
        vel.y = (vel.y / speed) * 2
        vel.z = (vel.z / speed) * 2
      }
      
      node.x += vel.x
      node.y += vel.y
      node.z += vel.z
      
      if (Math.abs(vel.x) > 0.01 || Math.abs(vel.y) > 0.01 || Math.abs(vel.z) > 0.01) {
        hasChanges = true
      }
    }

    if (hasChanges) {
      onNodesUpdate && onNodesUpdate([...currentNodes])
    }
  })

  return null
}

function Scene({ nodes, links, selectedNode, onSelectNode, hoveredNode, onHoverNode }) {
  const [displayNodes, setDisplayNodes] = useState(nodes)

  useEffect(() => {
    setDisplayNodes(nodes)
  }, [nodes])

  const handleNodesUpdate = useCallback((updated) => {
    setDisplayNodes(updated)
  }, [])

  const nodeMap = useMemo(() => {
    const map = {}
    displayNodes.forEach(n => { map[n.id] = n })
    return map
  }, [displayNodes])

  return (
    <>
      <ambientLight intensity={0.4} />
      <pointLight position={[10, 10, 10]} intensity={1} />
      <pointLight position={[-10, -10, -10]} intensity={0.3} />
      
      <PhysicsSimulation
        nodes={displayNodes}
        links={links}
        onNodesUpdate={handleNodesUpdate}
      />

      {links.map((link, idx) => {
        const source = nodeMap[link.source]
        const target = nodeMap[link.target]
        if (!source || !target) return null
        return <LinkLine key={idx} source={source} target={target} strength={link.strength} />
      })}

      {displayNodes.map(node => (
        <NodeSphere
          key={node.id}
          node={node}
          isSelected={selectedNode?.id === node.id}
          onClick={onSelectNode}
          isHovered={hoveredNode?.id === node.id}
          onHover={onHoverNode}
        />
      ))}

      {selectedNode && (
        <NodeLabel node={selectedNode} isVisible={true} />
      )}

      <Sparkles count={50} scale={200} size={4} speed={0.4} opacity={0.3} color="#6366f1" />
      
      <OrbitControls
        enableDamping
        dampingFactor={0.05}
        minDistance={20}
        maxDistance={300}
      />
    </>
  )
}

function Legend({ categories }) {
  return (
    <div className="topology-legend">
      <div className="legend-title">Categories</div>
      {categories.slice(0, 10).map(cat => (
        <div key={cat} className="legend-item">
          <span 
            className="legend-color" 
            style={{ background: `#${(CATEGORY_COLORS[cat] || 0x666666).toString(16).padStart(6, '0')}` }}
          />
          <span className="legend-label">{cat}</span>
        </div>
      ))}
    </div>
  )
}

function NodeDetails({ node, onClose }) {
  if (!node) return null

  const openUrl = () => {
    window.open(node.url, '_blank')
  }

  return (
    <div className="node-details-overlay" onClick={onClose}>
      <div className="node-details-card" onClick={e => e.stopPropagation()}>
        <div className="node-details-header">
          <span className="node-source-icon">{SOURCE_ICONS[node.source] || '📦'}</span>
          <div className="node-details-title">{node.title}</div>
          <button className="node-details-close" onClick={onClose}>×</button>
        </div>
        
        <div className="node-details-category">
          <span className="category-badge">{node.category || 'Uncategorized'}</span>
          <span className="match-score">{Math.round(node.match_score * 100)}% match</span>
        </div>

        {node.tags && node.tags.length > 0 && (
          <div className="node-details-tags">
            {node.tags.slice(0, 8).map(tag => (
              <span key={tag} className="tag-chip">{tag}</span>
            ))}
          </div>
        )}

        <div className="node-details-actions">
          <button className="btn btn-primary" onClick={openUrl}>
            Open Project ↗
          </button>
        </div>
      </div>
    </div>
  )
}

export default function Topology() {
  const [nodes, setNodes] = useState([])
  const [links, setLinks] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedNode, setSelectedNode] = useState(null)
  const [hoveredNode, setHoveredNode] = useState(null)
  const [source, setSource] = useState('')
  const [limit, setLimit] = useState(100)

  const fetchTopology = useCallback(async (src, lim) => {
    setLoading(true)
    try {
      const params = { limit: lim }
      if (src) params.source = src
      
      const [topologyRes, categoriesRes] = await Promise.all([
        getTopology(params),
        getCategories(),
      ])
      
      setNodes(topologyRes.data.nodes || [])
      setLinks(topologyRes.data.links || [])
      setCategories(categoriesRes.data || [])
    } catch (err) {
      console.error('Failed to fetch topology:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchTopology(source, limit)
  }, [source, limit, fetchTopology])

  return (
    <main className="topology-page">
      <div className="topology-header">
        <div>
          <div className="section-title">3D Topology View</div>
          <div className="section-sub">
            Explore projects as an interactive network. Click nodes to view details.
          </div>
        </div>
        
        <div className="topology-filters">
          <select value={source} onChange={e => setSource(e.target.value)}>
            <option value="">All Sources</option>
            <option value="github">GitHub Trending</option>
            <option value="hn">Hacker News</option>
            <option value="ph">Product Hunt</option>
          </select>
          
          <select value={limit} onChange={e => setLimit(Number(e.target.value))}>
            <option value={50}>50 nodes</option>
            <option value={100}>100 nodes</option>
            <option value={200}>200 nodes</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="topology-loading">
          <div className="spinner" />
          <p>Generating network topology...</p>
        </div>
      ) : nodes.length === 0 ? (
        <div className="empty">
          <div className="empty-icon">🌐</div>
          <p>No projects available for visualization. Try after the next crawl.</p>
        </div>
      ) : (
        <div className="topology-container">
          <div className="topology-canvas">
            <Canvas
              camera={{ position: [0, 0, 80], fov: 60 }}
              style={{ background: '#0a0a1a' }}
              onClick={() => setSelectedNode(null)}
            >
              <Scene
                nodes={nodes}
                links={links}
                selectedNode={selectedNode}
                onSelectNode={setSelectedNode}
                hoveredNode={hoveredNode}
                onHoverNode={setHoveredNode}
              />
            </Canvas>
            
            <div className="topology-stats">
              <div className="stat-item">
                <span className="stat-value">{nodes.length}</span>
                <span className="stat-label">Projects</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">{links.length}</span>
                <span className="stat-label">Connections</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">{categories.length}</span>
                <span className="stat-label">Categories</span>
              </div>
            </div>
          </div>
          
          <Legend categories={categories} />
        </div>
      )}

      <NodeDetails 
        node={selectedNode} 
        onClose={() => setSelectedNode(null)} 
      />
    </main>
  )
}
