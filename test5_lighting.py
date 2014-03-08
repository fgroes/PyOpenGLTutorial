from OpenGLContext import testingcontext
BaseContext = testingcontext.getInteractive()
from OpenGL.GL import *
from OpenGL.arrays import vbo
from OpenGLContext.arrays import *
from OpenGL.GL import shaders
from OpenGLContext.events.timer import Timer


class TestContext(BaseContext):
	"""Demonstrates the use of attribute types in GLSL"""

	def OnInit(self):
		"""Initialize the context"""
		phong_weight_calc = \
			"""
			float phong_weight_calc(in vec3 light_pos, in vec3 frag_normal)
			{
				float n_dot_pos = max(0.0, dot(frag_normal, light_pos));
				return n_dot_pos;
			}
			"""	
		vertex_shader = shaders.compileShader(phong_weight_calc +
			"""
			uniform vec4 global_ambient;
			uniform vec4 light_ambient;
			uniform vec4 light_diffuse;
			uniform vec3 light_location;
			uniform vec4 material_ambient;
			uniform vec4 material_diffuse;
			attribute vec3 vertex_position;
			attribute vec3 vertex_normal;
			varying vec4 base_color;
			void main()
			{
				gl_Position = gl_ModelViewProjectionMatrix * vec4(vertex_position, 1.0);
				vec3 ec_light_location = gl_NormalMatrix * light_location;
				float diffuse_weight = phong_weight_calc(
					normalize(ec_light_location), normalize(gl_NormalMatrix * vertex_normal));
				// also possible to do in model space, convention is eye space
				// vec2 weights = phong_weight_calc(
				// 	    normalize(light_location), normalize(vertex_normal));
				base_color = clamp(
					(global_ambient + light_ambient ) * material_ambient
					+ light_diffuse * material_diffuse * diffuse_weight, 0.0, 1.0);
			}
			""",
			GL_VERTEX_SHADER)
		fragment_shader = shaders.compileShader(
			"""
			varying vec4 base_color;
			void main()
			{
				gl_FragColor = base_color;
			}
			""",
			GL_FRAGMENT_SHADER)
		self.shader = shaders.compileProgram(vertex_shader, fragment_shader)
		self.vbo = vbo.VBO(
			array([
				[-1, 0, 0, -1, 0, 1],
				[0, 0, 1, -1, 0, 2],
				[0, 1, 1, -1, 0, 2],
				[-1, 0, 0, -1, 0, 1],
				[0, 1, 1, -1, 0, 2],
				[-1, 1, 0, -1, 0, 1],
				[0, 0, 1, -1, 0, 2],
				[1, 0, 1, 1, 0, 2],
				[1, 1, 1, 1, 0, 2],
				[0, 0, 1, -1, 0, 2],
				[1, 1, 1, 1, 0, 2],
				[0, 1, 1, -1, 0, 2],
				[1, 0, 1, 1, 0, 2],
				[2, 0, 0, 1, 0, 1],
				[2, 1, 0, 1, 0, 1],
				[1, 0, 1, 1, 0, 2],
				[2, 1, 0, 1, 0, 1],
				[1, 1, 1, 1, 0, 2]
				], "f"))
		for uniform in ("global_ambient", "light_ambient", "light_diffuse", "light_location",
				"material_ambient", "material_diffuse"):
			location = glGetUniformLocation(self.shader, uniform)
			if location in (None, -1):
				print("Warning, no uniform: {0}".format(uniform))
			setattr(self, uniform + "_location", location)
		for attribute in ("vertex_position", "vertex_normal"):
			location = glGetAttribLocation(self.shader, attribute)
			if location in (None, -1):
				print("Warning, no attribute: {0}".format(attribute))
			setattr(self, attribute + "_location", location)

	def Render(self, mode=0):
		"""Render the geometry for the scene."""
		super(TestContext, self).Render(mode)
		glUseProgram(self.shader)
		try:
			self.vbo.bind()
			try:
				glUniform4f(self.light_ambient_location, 0.2, 0.2, 0.2, 1.0)
				glUniform4f(self.light_diffuse_location, 1, 0.8, 0.8, 1)
				glUniform3f(self.light_location_location, 2, 2, 10)
				glUniform4f(self.material_ambient_location, 0.2, 0.2, 0.8, 1.0)
				glUniform4f(self.material_diffuse_location, 1, 1, 1, 1)
				glEnableVertexAttribArray(self.vertex_position_location)
				glEnableVertexAttribArray(self.vertex_normal_location)
				stride = 6 * 4
				glVertexAttribPointer(
					self.vertex_position_location, 
					3, GL_FLOAT, False, stride, self.vbo)
				glVertexAttribPointer(
					self.vertex_normal_location,
					3, GL_FLOAT, False, stride, self.vbo + 12)
				glDrawArrays(GL_TRIANGLES, 0, 18)
			finally:
				self.vbo.unbind()
				glDisableVertexAttribArray(self.vertex_position_location)
				glDisableVertexAttribArray(self.vertex_normal_location)
		finally:
			shaders.glUseProgram(0)


if __name__ == "__main__":
	TestContext.ContextMainLoop()
