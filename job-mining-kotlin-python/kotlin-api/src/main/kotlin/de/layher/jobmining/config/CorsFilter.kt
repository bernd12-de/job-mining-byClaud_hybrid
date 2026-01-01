package de.layher.jobmining.config

import jakarta.servlet.*
import jakarta.servlet.http.HttpServletRequest
import jakarta.servlet.http.HttpServletResponse
import org.springframework.core.Ordered
import org.springframework.core.annotation.Order
import org.springframework.stereotype.Component
import java.io.IOException

/**
 * CORS Filter für alle Requests
 * Behebt das "Failed to fetch" Problem in Swagger UI
 */
@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
class CorsFilter : Filter {

    @Throws(IOException::class, ServletException::class)
    override fun doFilter(req: ServletRequest, res: ServletResponse, chain: FilterChain) {
        val response = res as HttpServletResponse
        val request = req as HttpServletRequest

        response.setHeader("Access-Control-Allow-Origin", "*")
        response.setHeader("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS, PATCH")
        response.setHeader("Access-Control-Max-Age", "3600")
        response.setHeader("Access-Control-Allow-Headers", "*")
        response.setHeader("Access-Control-Allow-Credentials", "true")

        if ("OPTIONS".equals(request.method, ignoreCase = true)) {
            response.status = HttpServletResponse.SC_OK
        } else {
            chain.doFilter(req, res)
        }
    }
}
