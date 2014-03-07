from OpenGLContext import testingcontext
BaseContext = testingcontext.getInteractive()
from OpenGL.GL import *
from OpenGL.arrays import vbo
from OpenGLContext.arrays import *
from OpenGL.GL import shaders


class TestContext(BaseContext):
	"""
	This shader just passes gl_Color from an input array to
	the fragment shader, which interpolates the values across the
	fase (via a "varying" data type).
	"""

	def OnInit(self):
		"""Initialize the context once we have a valid OpenGL environ"""
		try:
			shaders.compileShader("""void main(){""", GL_VERTEX_SHADER)
		except RuntimeError, err:
			print("Example of shader compile error", err)
		else:
			raise RuntimeError("""Didn't catch compilation error!""")
		vertex_shader = shaders.compileShader(
			"""
			varying vec4 vertex_color;
			void main()
			{
				gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
				vertex_color = gl_Color;
			}
			""",
			GL_VERTEX_SHADER)
		fragment_shader = shaders.compileShader(
			"""
			varying vec4 vertex_color;
			void main()
			{
				gl_FragColor = vertex_color;
			}
			""",
			GL_FRAGMENT_SHADER)
		self.shader = shaders.compileProgram(vertex_shader, fragment_shader)
		self.vbo = vbo.VBO(
			array([
				[0, 1, 0, 0, 1, 0],
				[-1, -1, 0, 1, 1, 0],
				[1, -1, 0, 0, 1, 1],
				[2, -1, 0, 1, 0, 0],
				[4, -1, 0, 0, 1, 0],
				[4, 1, 0, 0, 0, 1],
				[2, -1, 0, 1, 0, 0],
				[4, 1, 0, 0, 0, 1],
				[2, 1, 0, 0, 1, 1]
				], "f"))

	def Render(self, mode):
		"""Render the geometry for the scene."""
		shaders.glUseProgram(self.shader)
		try:
			self.vbo.bind()
			try:
				glEnableClientState(GL_VERTEX_ARRAY)
				glEnableClientState(GL_COLOR_ARRAY)
				glVertexPointer(3, GL_FLOAT, 4 * 6, self.vbo)
				glColorPointer(3, GL_FLOAT, 4 * 6, self.vbo + 12)
				glDrawArrays(GL_TRIANGLES, 0, 9)
			finally:
				self.vbo.unbind()
				glDisableClientState(GL_VERTEX_ARRAY)
				glDisableClientState(GL_COLOR_ARRAY)
		finally:
			shaders.glUseProgram(0)


if __name__ == "__main__":
	TestContext.ContextMainLoop()
