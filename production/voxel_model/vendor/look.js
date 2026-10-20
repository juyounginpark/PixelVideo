// 쓸궁지 영상과 같은 화면 느낌: 장면을 한 번 그린 뒤 깊이 차이로 외곽선을 넣는다(public/main.js의 후처리와 같은 방식).
// mode 0 = 깔끔(외곽선 + 은은한 번짐), 1 = 레트로 TV(영상의 crt 스타일: 색 번짐·주사선·비네트)
import * as THREE from "three";

export function createLook(renderer, scene, camera) {
  const size = new THREE.Vector2();
  renderer.getDrawingBufferSize(size);
  const rt = new THREE.WebGLRenderTarget(size.x, size.y, { samples: 0 });
  rt.depthTexture = new THREE.DepthTexture(size.x, size.y);

  const post = new THREE.ShaderMaterial({
    uniforms: {
      tC: { value: rt.texture }, tD: { value: rt.depthTexture },
      res: { value: new THREE.Vector2(size.x, size.y) },
      near: { value: camera.near }, far: { value: camera.far },
      thick: { value: 1.5 }, mode: { value: 0 }, time: { value: 0 },
    },
    vertexShader: "varying vec2 v;void main(){v=uv;gl_Position=vec4(position.xy,0.,1.);}",
    fragmentShader: `
      precision highp float;
      varying vec2 v; uniform sampler2D tC,tD; uniform vec2 res; uniform float near,far,thick,time; uniform int mode;
      float lin(float d){return near*far/(far-(far-near)*d);}
      float hash(vec2 p){return fract(sin(dot(p,vec2(12.9898,78.233)))*43758.5453);}
      float edgeAt(vec2 uv){
        vec2 px=thick/res; float d=lin(texture2D(tD,uv).r); float e=0.;
        for(int i=0;i<8;i++){float a=float(i)*0.7854; vec2 o=vec2(cos(a),sin(a));
          float dn=lin(texture2D(tD,uv+o*px).r); e+=step(0.03*d+0.1,abs(dn-d));}
        return min(e*0.5,1.);}
      vec3 col(vec2 uv,float e){vec3 c=pow(texture2D(tC,uv).rgb,vec3(1./2.2)); return c*(1.-0.5*e);}
      void main(){
        float e=edgeAt(v); vec3 c;
        if(mode==1){
          float ca=0.0028*thick;
          c=vec3(col(v+vec2(ca,0.)/res*360.,e).r,col(v,e).g,col(v-vec2(ca,0.)/res*360.,e).b);
          vec3 bl=vec3(0.); for(int i=0;i<8;i++){float a=float(i)*0.785; bl+=col(v+vec2(cos(a),sin(a))*vec2(0.006,0.0034),e);}
          c+=(bl/8.)*0.25;
          c*=0.86+0.14*sin(gl_FragCoord.y*3.14159/max(2.,thick*2.));
          c*=vec3(0.97,1.01,1.05);
          c+=(hash(gl_FragCoord.xy+time)-0.5)*0.04;
          vec2 q=v-0.5; c*=1.-dot(q,q)*0.9;
        } else {
          c=col(v,e);
          vec3 bl=vec3(0.); for(int i=0;i<8;i++){float a=float(i)*0.785; bl+=max(col(v+vec2(cos(a),sin(a))*4.*thick/res,0.)-vec3(.8),0.);}
          c+=bl/8.*0.6;
        }
        gl_FragColor=vec4(clamp(c,0.,1.),1.);}`,
    depthTest: false, depthWrite: false,
  });
  const postScene = new THREE.Scene();
  postScene.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), post));
  const postCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

  return {
    set mode(m) { post.uniforms.mode.value = m; },
    get mode() { return post.uniforms.mode.value; },
    render(time = 0) {
      renderer.getDrawingBufferSize(size);
      if (rt.width !== size.x || rt.height !== size.y) {
        rt.setSize(size.x, size.y);
        post.uniforms.res.value.copy(size);
      }
      post.uniforms.thick.value = Math.max(1, renderer.getPixelRatio() * 0.9);
      post.uniforms.near.value = camera.near; post.uniforms.far.value = camera.far;
      post.uniforms.time.value = time;
      renderer.setRenderTarget(rt);
      renderer.render(scene, camera);
      renderer.setRenderTarget(null);
      renderer.render(postScene, postCam);
    },
  };
}
