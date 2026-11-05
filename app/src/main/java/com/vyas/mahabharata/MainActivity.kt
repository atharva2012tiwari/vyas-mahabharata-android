package com.vyas.mahabharata

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.navigation.compose.rememberNavController
import com.vyas.mahabharata.data.local.VyasDatabase
import com.vyas.mahabharata.data.repository.MahabharataRepositoryImpl
import com.vyas.mahabharata.ui.navigation.VyasNavHost
import com.vyas.mahabharata.ui.theme.VyasTheme

/**
 * Main Activity for Vyasa Mahabharata Scripture Reading Application.
 * Configured with Material 3 Expressive, edge-to-edge reading canvas, and Room persistence.
 */
class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        // Initialize Room Database & Repository Layer
        val database = VyasDatabase.getInstance(applicationContext)
        val repository = MahabharataRepositoryImpl(database)

        setContent {
            VyasTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    val navController = rememberNavController()
                    VyasNavHost(
                        navController = navController,
                        repository = repository
                    )
                }
            }
        }
    }
}
