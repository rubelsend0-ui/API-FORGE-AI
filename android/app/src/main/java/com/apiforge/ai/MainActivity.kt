package com.apiforge.ai

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import com.apiforge.ai.ui.navigation.ApiForgeNavGraph
import com.apiforge.ai.ui.theme.ApiForgeTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            ApiForgeTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    ApiForgeNavGraph()
                }
            }
        }
    }
}
